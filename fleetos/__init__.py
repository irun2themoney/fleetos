"""
FleetOS: Kubernetes-style orchestration for autonomous agents.

A free, open-source framework that turns OpenClaw agents into a complete
business operating system for solo founders.
"""

__version__ = "0.2.0"
__author__ = "FleetOS Contributors"
__license__ = "MIT"

# Core imports — lazy to avoid circular deps and missing optional packages
try:
    from fleetos.cli import cli as cli_main
except Exception:
    cli_main = None  # type: ignore

try:
    from fleetos.core.planner import Planner
except Exception:
    Planner = None  # type: ignore

try:
    from fleetos.core.orchestrator import Orchestrator
except Exception:
    Orchestrator = None  # type: ignore

try:
    from fleetos.core.memory import Memory as MemoryManager
except Exception:
    MemoryManager = None  # type: ignore

try:
    from fleetos.core.verifier import Verifier
except Exception:
    Verifier = None  # type: ignore

__all__ = [
    "cli_main",
    "Planner",
    "Orchestrator",
    "MemoryManager",
    "Verifier",
]
