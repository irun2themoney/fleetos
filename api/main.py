"""
FleetOS API — FastAPI backend

Endpoints:
  POST /api/run          — start a fleet run (returns stream of events)
  GET  /api/runs         — list user's past runs
  GET  /api/runs/{id}    — get a specific run
  POST /api/auth/signup  — create account
  POST /api/auth/login   — login, returns JWT
  POST /api/billing/checkout — create Stripe checkout session
  GET  /api/billing/portal   — Stripe customer portal URL
  GET  /api/health       — health check
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

# JWT
try:
    import jwt as pyjwt
except ImportError:
    pyjwt = None  # type: ignore

# Stripe
try:
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
except ImportError:
    stripe = None  # type: ignore

# Password hashing
try:
    import bcrypt as _bcrypt_lib
    _bcrypt_available = True
except ImportError:
    _bcrypt_lib = None  # type: ignore
    _bcrypt_available = False

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fleetos.api")

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="FleetOS API",
    description="Autonomous AI business fleet — REST API",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

JWT_SECRET = os.getenv("JWT_SECRET", "fleetos-dev-secret-change-in-prod")
JWT_EXPIRY_HOURS = 72

# ---------------------------------------------------------------------------
# In-memory stores (replace with Postgres in production)
# ---------------------------------------------------------------------------

_users: Dict[str, Dict] = {}       # email → user dict
_runs: Dict[str, Dict] = {}        # run_id → run dict
_sessions: Dict[str, str] = {}     # token → email

# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def _hash_password(pw: str) -> str:
    if _bcrypt_available:
        return _bcrypt_lib.hashpw(pw.encode(), _bcrypt_lib.gensalt()).decode()
    import hashlib
    return hashlib.sha256(pw.encode()).hexdigest()

def _verify_password(pw: str, hashed: str) -> bool:
    if _bcrypt_available:
        return _bcrypt_lib.checkpw(pw.encode(), hashed.encode())
    import hashlib
    return hashlib.sha256(pw.encode()).hexdigest() == hashed

def _create_token(email: str) -> str:
    if pyjwt:
        payload = {
            "sub": email,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
            "iat": datetime.utcnow(),
        }
        return pyjwt.encode(payload, JWT_SECRET, algorithm="HS256")
    # Fallback: simple token
    token = str(uuid.uuid4())
    _sessions[token] = email
    return token

def _decode_token(token: str) -> Optional[str]:
    if pyjwt:
        try:
            payload = pyjwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return payload.get("sub")
        except Exception:
            return None
    return _sessions.get(token)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    email = _decode_token(credentials.credentials)
    if not email or email not in _users:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return _users[email]

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str = ""

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RunRequest(BaseModel):
    command: str
    template: Optional[str] = None
    auto_approve: bool = True

class ApproveRequest(BaseModel):
    run_id: str
    approved: bool

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.2.0", "timestamp": datetime.utcnow().isoformat()}

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.post("/api/auth/signup")
async def signup(req: SignupRequest):
    if req.email in _users:
        raise HTTPException(status_code=400, detail="Email already registered")

    _users[req.email] = {
        "email": req.email,
        "name": req.name,
        "password_hash": _hash_password(req.password),
        "created_at": datetime.utcnow().isoformat(),
        "plan": "free",          # free | pro
        "runs_this_month": 0,
        "stripe_customer_id": None,
    }

    token = _create_token(req.email)
    logger.info(f"New user: {req.email}")
    return {"token": token, "user": {"email": req.email, "name": req.name, "plan": "free"}}


@app.post("/api/auth/login")
async def login(req: LoginRequest):
    user = _users.get(req.email)
    if not user or not _verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = _create_token(req.email)
    return {
        "token": token,
        "user": {"email": user["email"], "name": user["name"], "plan": user["plan"]},
    }


@app.get("/api/auth/me")
async def me(user: Dict = Depends(get_current_user)):
    return {"email": user["email"], "name": user["name"], "plan": user["plan"]}

# ---------------------------------------------------------------------------
# Fleet runs
# ---------------------------------------------------------------------------

FREE_RUN_LIMIT = 3  # free users get 3 runs/month

@app.post("/api/run")
async def start_run(req: RunRequest, user: Dict = Depends(get_current_user)):
    """Start a fleet run. Returns server-sent events stream."""

    # Enforce free tier limit
    if user["plan"] == "free" and user["runs_this_month"] >= FREE_RUN_LIMIT:
        raise HTTPException(
            status_code=402,
            detail=f"Free plan limit ({FREE_RUN_LIMIT} runs/month) reached. Upgrade to Pro."
        )

    run_id = f"run_{uuid.uuid4().hex[:8]}"
    run = {
        "id": run_id,
        "user": user["email"],
        "command": req.command,
        "template": req.template,
        "status": "starting",
        "created_at": datetime.utcnow().isoformat(),
        "events": [],
        "result": None,
    }
    _runs[run_id] = run
    user["runs_this_month"] += 1

    return StreamingResponse(
        _stream_run(run_id, req.command, req.template, req.auto_approve),
        media_type="text/event-stream",
        headers={"X-Run-Id": run_id},
    )


async def _stream_run(
    run_id: str,
    command: str,
    template: Optional[str],
    auto_approve: bool,
) -> AsyncGenerator[str, None]:
    """Stream run events as server-sent events."""

    def _event(event_type: str, data: Any) -> str:
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

    try:
        yield _event("status", {"run_id": run_id, "status": "starting", "message": "Initialising fleet…"})
        await asyncio.sleep(0.1)

        # Import graph
        from fleetos.core.graph import build_graph
        graph = build_graph()

        yield _event("status", {"run_id": run_id, "status": "planning", "message": "Parsing command and selecting template…"})
        await asyncio.sleep(0.2)

        state = {
            "raw_command": command,
            "session_id": run_id,
            "approved": auto_approve,
        }
        if template:
            state["template_name"] = template

        yield _event("status", {"run_id": run_id, "status": "executing", "message": "Agents running in parallel…"})

        # Run in thread to not block event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, graph.invoke, state)

        # Stream individual agent results
        for artifact in result.get("results", []):
            yield _event("artifact", {
                "run_id": run_id,
                "role": artifact.get("role"),
                "output": str(artifact.get("artifact") or artifact.get("output") or "")[:2000],
            })
            await asyncio.sleep(0.05)

        # Final result
        _runs[run_id]["status"] = result.get("status", "success")
        _runs[run_id]["result"] = result
        _runs[run_id]["completed_at"] = datetime.utcnow().isoformat()

        yield _event("complete", {
            "run_id": run_id,
            "status": result.get("status"),
            "summary": result.get("summary", ""),
            "agents": len(result.get("agents", [])),
            "artifacts": len(result.get("results", [])),
            "confidence": result.get("confidence", 0),
        })

    except Exception as exc:
        logger.exception(f"Run {run_id} failed: {exc}")
        _runs[run_id]["status"] = "failed"
        yield _event("error", {"run_id": run_id, "error": str(exc)})


@app.get("/api/runs")
async def list_runs(user: Dict = Depends(get_current_user)):
    user_runs = [
        {
            "id": r["id"],
            "command": r["command"],
            "status": r["status"],
            "created_at": r["created_at"],
            "completed_at": r.get("completed_at"),
        }
        for r in _runs.values()
        if r["user"] == user["email"]
    ]
    return {"runs": sorted(user_runs, key=lambda x: x["created_at"], reverse=True)}


@app.get("/api/runs/{run_id}")
async def get_run(run_id: str, user: Dict = Depends(get_current_user)):
    run = _runs.get(run_id)
    if not run or run["user"] != user["email"]:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

# ---------------------------------------------------------------------------
# Billing (Stripe)
# ---------------------------------------------------------------------------

STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")  # your Pro plan price ID
APP_URL = os.getenv("APP_URL", "http://localhost:3000")

@app.post("/api/billing/checkout")
async def create_checkout(user: Dict = Depends(get_current_user)):
    if not stripe:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    session = stripe.checkout.Session.create(
        customer_email=user["email"],
        payment_method_types=["card"],
        line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
        mode="subscription",
        success_url=f"{APP_URL}/dashboard?upgraded=true",
        cancel_url=f"{APP_URL}/pricing",
        metadata={"user_email": user["email"]},
    )
    return {"url": session.url}


@app.post("/api/billing/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events (subscription activated, cancelled, etc.)"""
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig, webhook_secret)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if event["type"] == "checkout.session.completed":
        email = event["data"]["object"]["metadata"].get("user_email")
        if email and email in _users:
            _users[email]["plan"] = "pro"
            _users[email]["stripe_customer_id"] = event["data"]["object"]["customer"]
            logger.info(f"Upgraded to Pro: {email}")

    elif event["type"] in ("customer.subscription.deleted", "customer.subscription.paused"):
        customer_id = event["data"]["object"]["customer"]
        for user in _users.values():
            if user.get("stripe_customer_id") == customer_id:
                user["plan"] = "free"
                logger.info(f"Downgraded to free: {user['email']}")

    return {"received": True}


@app.get("/api/billing/portal")
async def billing_portal(user: Dict = Depends(get_current_user)):
    if not stripe or not user.get("stripe_customer_id"):
        raise HTTPException(status_code=400, detail="No billing account found")

    session = stripe.billing_portal.Session.create(
        customer=user["stripe_customer_id"],
        return_url=f"{APP_URL}/dashboard",
    )
    return {"url": session.url}


# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
