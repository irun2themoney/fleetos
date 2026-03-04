"""FleetOS agent registry — maps role names to concrete agent classes."""

from fleetos.agents.base import BaseAgent, AgentResult
from fleetos.agents.strategy import StrategyAgent
from fleetos.agents.content import ContentAgent
from fleetos.agents.marketing import MarketingAgent
from fleetos.agents.finance import FinanceAgent
from fleetos.agents.research import ResearchAgent

AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    "Strategy": StrategyAgent,
    "Content": ContentAgent,
    "SEO": ContentAgent,          # reuse content agent for SEO tasks
    "Marketing": MarketingAgent,
    "Finance": FinanceAgent,
    "Research": ResearchAgent,
    "Lead_Research": ResearchAgent,
    "Sales": StrategyAgent,       # strategy agent handles sales planning
    "Outreach": ContentAgent,     # content agent drafts outreach copy
    "Delivery": StrategyAgent,
    "Support": ContentAgent,
}


def get_agent(role: str, **kwargs) -> BaseAgent:
    """
    Instantiate an agent for the given role.

    Args:
        role:   Role name (e.g. "Strategy", "Content").
        **kwargs: Passed to the agent constructor.

    Returns:
        Concrete BaseAgent subclass instance.
    """
    cls = AGENT_REGISTRY.get(role, StrategyAgent)
    instance = cls(**kwargs)
    instance.name = role  # preserve the role label for logging/output
    return instance


__all__ = [
    "BaseAgent",
    "AgentResult",
    "StrategyAgent",
    "ContentAgent",
    "MarketingAgent",
    "FinanceAgent",
    "ResearchAgent",
    "AGENT_REGISTRY",
    "get_agent",
]
