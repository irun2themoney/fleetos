"""Strategy Agent — builds 30/60/90-day business plans."""

from __future__ import annotations
from fleetos.agents.base import BaseAgent, AgentResult


class StrategyAgent(BaseAgent):
    name = "Strategy"

    async def run(self, task: str, context: str) -> AgentResult:
        system = (
            "You are a world-class business strategist specialising in bootstrapped "
            "online businesses. Output concise, numbered action plans with clear "
            "milestones, KPIs, and timeline estimates. Be specific and actionable."
        )
        output = await self.call_llm(system, task)
        return AgentResult(role=self.name, output=output)
