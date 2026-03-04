"""
Base agent class for all FleetOS agents.

Every specialised agent (Content, Strategy, Marketing, etc.) inherits from
BaseAgent and implements the `run()` method.  The orchestrator calls agents
through this uniform interface so it never needs to know the concrete type.
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AgentResult:
    """Typed container for agent execution results."""

    __slots__ = ("role", "output", "status", "error", "metadata", "timestamp")

    def __init__(
        self,
        role: str,
        output: Optional[str] = None,
        status: str = "success",
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.role = role
        self.output = output
        self.status = status
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "output": self.output,
            "status": self.status,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }

    def __repr__(self) -> str:
        return f"<AgentResult role={self.role!r} status={self.status!r}>"


class BaseAgent(ABC):
    """
    Abstract base class for FleetOS agents.

    Subclasses must implement `run()`.  Optional hooks:
      - `before_run()` — setup / context loading
      - `after_run()` — cleanup / artifact saving
    """

    #: Override in subclasses to set a human-readable name
    name: str = "BaseAgent"

    def __init__(
        self,
        ollama_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120,
    ):
        self.ollama_url = ollama_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1")
        self.timeout = timeout
        self._logger = logging.getLogger(f"fleetos.agents.{self.name}")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def execute(self, task: str, context: str = "") -> AgentResult:
        """
        Full execution lifecycle: before → run → after.

        Args:
            task:    The specific task prompt for this agent.
            context: Extra context (original user command, prior artifacts…).

        Returns:
            AgentResult with output or error information.
        """
        self._logger.info(f"[{self.name}] Starting: {task[:80]!r}")

        try:
            await self.before_run(task, context)
            result = await self.run(task, context)
            await self.after_run(result)
            self._logger.info(f"[{self.name}] Finished with status={result.status!r}")
            return result

        except Exception as exc:
            self._logger.exception(f"[{self.name}] Unhandled exception: {exc}")
            return AgentResult(
                role=self.name,
                status="failed",
                error=str(exc),
            )

    # ------------------------------------------------------------------
    # Hooks (override as needed)
    # ------------------------------------------------------------------

    async def before_run(self, task: str, context: str) -> None:
        """Called before run().  Override for setup logic."""

    async def after_run(self, result: AgentResult) -> None:
        """Called after run().  Override for cleanup / persistence."""

    # ------------------------------------------------------------------
    # Abstract
    # ------------------------------------------------------------------

    @abstractmethod
    async def run(self, task: str, context: str) -> AgentResult:
        """
        Execute the agent's core logic.

        Args:
            task:    Specific task description.
            context: Broader business context.

        Returns:
            AgentResult
        """

    # ------------------------------------------------------------------
    # Shared LLM helper
    # ------------------------------------------------------------------

    async def call_llm(self, system: str, user: str) -> str:
        """
        Call the local Ollama LLM and return the response text.

        Tries aiohttp first, falls back to urllib if unavailable.
        """
        try:
            import aiohttp

            payload = {
                "model": self.model,
                "prompt": f"System: {system}\n\nUser: {user}",
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 768},
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("response", "").strip()
                    text = await resp.text()
                    raise RuntimeError(f"Ollama {resp.status}: {text[:200]}")

        except ImportError:
            return await self._urllib_call(system, user)

        except Exception as exc:
            self._logger.warning(f"LLM call failed: {exc} — using stub")
            return self._stub_response()

    async def _urllib_call(self, system: str, user: str) -> str:
        """urllib fallback for Ollama."""
        import asyncio
        import json
        import urllib.request

        payload = json.dumps({
            "model": self.model,
            "prompt": f"System: {system}\n\nUser: {user}",
            "stream": False,
        }).encode()

        req = urllib.request.Request(
            f"{self.ollama_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        loop = asyncio.get_event_loop()

        def _blocking():
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read()).get("response", "").strip()

        return await loop.run_in_executor(None, _blocking)

    def _stub_response(self) -> str:
        """Safe stub used when the LLM is unreachable."""
        return f"[{self.name}] LLM unavailable — stub response generated at {datetime.utcnow().isoformat()}"
