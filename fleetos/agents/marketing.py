"""Marketing Agent — channel strategy, launch plans, ad copy."""

from __future__ import annotations
from fleetos.agents.base import BaseAgent, AgentResult


class MarketingAgent(BaseAgent):
    name = "Marketing"

    async def run(self, task: str, context: str) -> AgentResult:
        system = (
            "You are a growth marketing expert who has scaled multiple bootstrapped "
            "businesses. Output multi-channel marketing plans with specific tactics, "
            "budget allocations, and measurable goals. Focus on low-cost, high-ROI channels."
        )
        output = await self.call_llm(system, task)
        return AgentResult(role=self.name, output=output)
