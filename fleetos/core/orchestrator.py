"""
Orchestrator: Spawns and manages OpenClaw agent workers.

Handles agent lifecycle: creation, execution, monitoring, and cleanup.
Supports parallel execution with timeout enforcement and error recovery.
"""

import asyncio
import subprocess
import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class AgentTask:
    """Represents a task for an agent to execute."""
    role: str
    task: str
    timeout: int = 300  # seconds
    retries: int = 3


class Orchestrator:
    """
    Orchestrates parallel execution of OpenClaw agents.

    Example:
        orchestrator = Orchestrator()
        results = orchestrator.run_parallel(agents, tasks)
    """

    def __init__(self, max_parallel: int = 4, timeout: int = 300):
        """
        Initialize orchestrator.

        Args:
            max_parallel: Maximum parallel agents (default: 4)
            timeout: Default timeout per agent in seconds
        """
        self.max_parallel = max_parallel
        self.timeout = timeout
        self.active_agents = {}
        logger.info(f"Orchestrator initialized (max {max_parallel} parallel agents)")

    async def run_parallel(
        self,
        agents: List[Dict[str, str]],
        command: str
    ) -> Dict[str, Any]:
        """
        Run agents in parallel.

        Args:
            agents: List of agent role specifications
            command: Original command context

        Returns:
            Dictionary with results from all agents
        """
        logger.info(f"Running {len(agents)} agents in parallel")

        tasks = [
            self._execute_agent(
                agent["role"],
                agent["task"],
                command
            )
            for agent in agents
        ]

        # Run all agents concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        aggregated = self._aggregate_results(agents, results)
        logger.info(f"All agents completed. Aggregated {len(aggregated)} artifacts")

        return aggregated

    async def _execute_agent(
        self,
        role: str,
        task: str,
        context: str,
        retries: int = 3
    ) -> Dict[str, Any]:
        """
        Execute a single OpenClaw agent with retry logic.

        Args:
            role: Agent role
            task: Task description
            context: Command context
            retries: Number of retry attempts

        Returns:
            Agent execution result
        """
        for attempt in range(retries):
            try:
                logger.info(f"[{role}] Executing task (attempt {attempt + 1}/{retries})")

                # Phase 1: Subprocess execution (direct OpenClaw call)
                # Phase 2+: Will be replaced with proper OpenClaw API integration
                result = await asyncio.wait_for(
                    self._run_openclaw_agent(role, task, context),
                    timeout=self.timeout
                )

                logger.info(f"[{role}] Completed successfully")
                return {
                    "role": role,
                    "task": task,
                    "output": result,
                    "status": "success",
                    "timestamp": datetime.utcnow().isoformat()
                }

            except asyncio.TimeoutError:
                logger.warning(f"[{role}] Timeout on attempt {attempt + 1}/{retries}")
                if attempt == retries - 1:
                    return {
                        "role": role,
                        "task": task,
                        "error": "timeout",
                        "status": "failed",
                        "timestamp": datetime.utcnow().isoformat()
                    }

            except Exception as e:
                logger.error(f"[{role}] Error on attempt {attempt + 1}/{retries}: {e}")
                if attempt == retries - 1:
                    return {
                        "role": role,
                        "task": task,
                        "error": str(e),
                        "status": "failed",
                        "timestamp": datetime.utcnow().isoformat()
                    }

        # Should not reach here
        return {
            "role": role,
            "task": task,
            "error": "max_retries_exceeded",
            "status": "failed",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _run_openclaw_agent(self, role: str, task: str, context: str) -> str:
        """
        Run OpenClaw agent via subprocess.

        Args:
            role: Agent role
            task: Task description
            context: Additional context

        Returns:
            Agent output
        """
        # Phase 1: Mock implementation
        # Phase 2+: Replace with actual OpenClaw CLI integration
        prompt = f"Role: {role}\nTask: {task}\nContext: {context}"

        # Mock delay
        await asyncio.sleep(0.5)

        # Mock output
        return f"[{role}] Completed: {task}"

    def _aggregate_results(
        self,
        agents: List[Dict[str, str]],
        results: List[Any]
    ) -> Dict[str, Any]:
        """
        Aggregate results from all agents.

        Args:
            agents: Original agent list
            results: Results from execution

        Returns:
            Aggregated results dictionary
        """
        aggregated = {
            "agents_executed": len(agents),
            "artifacts": [],
            "errors": [],
            "completed_at": datetime.utcnow().isoformat()
        }

        for agent, result in zip(agents, results):
            if isinstance(result, Exception):
                aggregated["errors"].append({
                    "role": agent["role"],
                    "error": str(result)
                })
            elif isinstance(result, dict):
                aggregated["artifacts"].append(result)

        return aggregated

    def cleanup(self):
        """Clean up active agents and resources."""
        logger.info(f"Cleaning up {len(self.active_agents)} active agents")
        self.active_agents.clear()


# TODO: Phase 2 - Integrate with real OpenClaw API
# TODO: Phase 2 - Add agent monitoring and health checks
# TODO: Phase 3 - Add adaptive parallelism based on resource usage
