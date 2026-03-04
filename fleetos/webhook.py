"""
FleetOS Telegram Approval Webhook Server.

Listens for Telegram callback queries so you can approve / reject fleet runs
from your phone with a single tap.

Run with:
    python -m fleetos.webhook

Environment variables required:
    TELEGRAM_BOT_TOKEN  — BotFather token
    TELEGRAM_CHAT_ID    — Your personal chat ID (or group ID)
    WEBHOOK_PORT        — Port to listen on (default 8443)
    WEBHOOK_SECRET      — Random string Telegram sends in X-Telegram-Bot-Api-Secret-Token header

Telegram setup:
    1. Create bot via @BotFather → /newbot
    2. Set webhook:
       curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://<your-domain>/webhook&secret_token=<SECRET>"
    3. Set TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID in .env
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory store for pending approvals
# ---------------------------------------------------------------------------

_pending: Dict[str, Dict[str, Any]] = {}   # run_id → state dict
_callbacks: Dict[str, asyncio.Future] = {}  # run_id → Future[bool]


def register_pending_run(run_id: str, state: Dict[str, Any]) -> asyncio.Future:
    """
    Register a fleet run that needs human approval.

    Returns a Future that resolves to True (approved) or False (rejected)
    when the user responds via Telegram.
    """
    loop = asyncio.get_event_loop()
    future: asyncio.Future = loop.create_future()
    _pending[run_id] = state
    _callbacks[run_id] = future
    logger.info(f"[webhook] Registered pending run: {run_id}")
    return future


def resolve_run(run_id: str, approved: bool):
    """Resolve a pending run's future (called from the HTTP handler)."""
    future = _callbacks.pop(run_id, None)
    _pending.pop(run_id, None)
    if future and not future.done():
        future.get_event_loop().call_soon_threadsafe(future.set_result, approved)
    logger.info(f"[webhook] Run {run_id} → {'approved' if approved else 'rejected'}")


# ---------------------------------------------------------------------------
# Telegram API helpers
# ---------------------------------------------------------------------------

def _tg_request(method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Send a request to the Telegram Bot API."""
    import urllib.request

    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not set — skipping Telegram call")
        return {}

    url = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as exc:
        logger.error(f"Telegram API error ({method}): {exc}")
        return {}


def send_approval_request(run_id: str, state: Dict[str, Any]) -> None:
    """
    Send an approval request message with Approve / Reject buttons to Telegram.
    """
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not chat_id:
        logger.warning("TELEGRAM_CHAT_ID not set — cannot send approval request")
        return

    command = state.get("raw_command", "?")[:200]
    confidence = state.get("confidence", 0)
    risk = state.get("risk_level", "unknown").upper()
    agents = [a["role"] for a in state.get("agents", [])]

    text = (
        f"⏸️ *FleetOS Approval Required*\n\n"
        f"*Run ID:* `{run_id}`\n"
        f"*Command:* {command}\n"
        f"*Confidence:* {confidence:.0f}/100\n"
        f"*Risk:* {risk}\n"
        f"*Agents:* {', '.join(agents)}\n\n"
        f"Tap below to approve or reject this run."
    )

    keyboard = {
        "inline_keyboard": [[
            {"text": "✅ Approve", "callback_data": f"approve:{run_id}"},
            {"text": "❌ Reject",  "callback_data": f"reject:{run_id}"},
        ]]
    }

    _tg_request("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": keyboard,
    })
    logger.info(f"[webhook] Approval request sent for run {run_id}")


def answer_callback(callback_query_id: str, text: str) -> None:
    """Acknowledge a Telegram callback query (removes loading spinner)."""
    _tg_request("answerCallbackQuery", {
        "callback_query_id": callback_query_id,
        "text": text,
        "show_alert": False,
    })


# ---------------------------------------------------------------------------
# HTTP webhook handler
# ---------------------------------------------------------------------------

class TelegramWebhookHandler(BaseHTTPRequestHandler):
    """Minimal HTTP server that receives Telegram webhook POST requests."""

    def log_message(self, fmt, *args):
        logger.debug(f"[webhook HTTP] {fmt % args}")

    def do_GET(self):
        """Health check endpoint."""
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/webhook":
            self._send_json(404, {"error": "not found"})
            return

        # Validate secret token
        secret = os.getenv("WEBHOOK_SECRET", "")
        if secret:
            received = self.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
            if not hmac.compare_digest(received, secret):
                logger.warning("[webhook] Invalid secret token")
                self._send_json(403, {"error": "forbidden"})
                return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            update = json.loads(body)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid json"})
            return

        self._handle_update(update)
        self._send_json(200, {"ok": True})

    def _handle_update(self, update: Dict[str, Any]) -> None:
        """Process an incoming Telegram update."""
        callback = update.get("callback_query")
        if not callback:
            return

        callback_id = callback.get("id", "")
        data = callback.get("data", "")

        if ":" not in data:
            return

        action, run_id = data.split(":", 1)
        approved = action == "approve"

        if run_id in _pending:
            resolve_run(run_id, approved)
            answer_callback(callback_id, "✅ Approved!" if approved else "❌ Rejected")
            logger.info(f"[webhook] {action}d run {run_id} via Telegram")
        else:
            answer_callback(callback_id, "Run not found (may have expired)")

    def _send_json(self, code: int, body: Dict[str, Any]) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


# ---------------------------------------------------------------------------
# Server lifecycle
# ---------------------------------------------------------------------------

_server: Optional[HTTPServer] = None
_server_thread: Optional[Thread] = None


def start_webhook_server(port: Optional[int] = None) -> None:
    """Start the webhook HTTP server in a background daemon thread."""
    global _server, _server_thread

    port = port or int(os.getenv("WEBHOOK_PORT", "8443"))

    _server = HTTPServer(("0.0.0.0", port), TelegramWebhookHandler)
    _server_thread = Thread(target=_server.serve_forever, daemon=True)
    _server_thread.start()
    logger.info(f"[webhook] Server started on port {port}")


def stop_webhook_server() -> None:
    """Gracefully shut down the webhook server."""
    global _server
    if _server:
        _server.shutdown()
        _server = None
        logger.info("[webhook] Server stopped")


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.getenv("WEBHOOK_PORT", "8443"))

    logger.info(f"Starting FleetOS webhook server on port {port}")
    logger.info("Health check: GET /health")
    logger.info("Telegram updates: POST /webhook")

    server = HTTPServer(("0.0.0.0", port), TelegramWebhookHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down…")
        server.shutdown()
