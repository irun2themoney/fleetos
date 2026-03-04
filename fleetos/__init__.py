"""
FleetOS: Kubernetes-style orchestration for autonomous agents.

A free, open-source framework that turns OpenClaw agents into a complete
business operating system for solo founders.
"""

__version__ = "0.1.0"
__author__ = "FleetOS Contributors"
__license__ = "MIT"

# Core imports
from fleetos.cli import main as cli_main
from fleetos.core.planner import Planner
from fleetos.core.orchestrator import Orchestrator
from fleetos.core.memory import MemoryManager
from fleetos.core.verifier import Verifier

__all__ = [
    "cli_main",
    "Planner",
    "Orchestrator",
    "MemoryManager",
    "Verifier",
]
