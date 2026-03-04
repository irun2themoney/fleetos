"""
Planner: Decomposes user commands into agent roles and tasks.

Uses LangGraph to build a hierarchical planning DAG that transforms
a natural language command into a structured fleet decomposition.
"""

from typing import TypedDict, List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class FleetState(TypedDict):
    """State dict for LangGraph DAG execution."""
    command: str
    template: Dict[str, Any]
    agents: List[Dict[str, str]]
    memory: Dict[str, Any]
    artifacts: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    needs_human_approval: bool
    approved_by: str
    completed_at: datetime


class Planner:
    """
    Decomposes high-level user commands into structured agent roles.

    Example:
        planner = Planner()
        roles = planner.decompose(
            "Launch my newsletter to $15k MRR in 90 days",
            template=newsletter_template
        )
        # Returns: ["Strategy", "Content", "Marketing", "Sales", "Finance", "Support"]
    """

    def __init__(self, llm=None):
        """
        Initialize planner.

        Args:
            llm: Language model instance (defaults to Ollama)
        """
        self.llm = llm
        logger.info("Planner initialized")

    def decompose(self, command: str, template: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Decompose a user command into agent roles.

        Args:
            command: User's natural language command
            template: Business template with predefined roles

        Returns:
            List of agent role specifications
        """
        logger.info(f"Decomposing command: {command}")

        # Phase 1: Use template roles as default
        agents = [
            {"role": role, "task": self._generate_task(role, command)}
            for role in template.get("roles", [])
        ]

        logger.info(f"Decomposed into {len(agents)} roles: {[a['role'] for a in agents]}")
        return agents

    def _generate_task(self, role: str, command: str) -> str:
        """
        Generate a specific task for an agent role.

        Args:
            role: Agent role (e.g., "Strategy")
            command: Original user command

        Returns:
            Task prompt for the agent
        """
        # Template task prompts by role
        role_prompts = {
            "Strategy": f"Analyze the following business goal and create a strategic plan: {command}",
            "Content": f"Create compelling content for: {command}",
            "Marketing": f"Plan a marketing campaign for: {command}",
            "Sales": f"Develop a sales strategy for: {command}",
            "Finance": f"Create financial projections for: {command}",
            "Support": f"Design customer support systems for: {command}",
        }

        return role_prompts.get(role, f"Execute the following task: {command}")

    def validate_decomposition(self, agents: List[Dict[str, str]]) -> bool:
        """
        Validate that decomposition is complete and coherent.

        Args:
            agents: List of agent role specifications

        Returns:
            True if valid, False otherwise
        """
        if not agents:
            logger.warning("Empty agent list")
            return False

        if len(agents) > 20:
            logger.warning(f"Too many agents: {len(agents)} > 20")
            return False

        required_fields = {"role", "task"}
        for agent in agents:
            if not all(field in agent for field in required_fields):
                logger.warning(f"Invalid agent spec: {agent}")
                return False

        logger.info(f"Decomposition valid: {len(agents)} agents")
        return True


# TODO: Phase 2 - Integrate with LangGraph
# TODO: Phase 2 - Add LLM-based decomposition
# TODO: Phase 3 - Add learning from past decompositions
