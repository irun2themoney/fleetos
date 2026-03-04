"""Finance Agent — revenue models, cash flow projections, pricing."""

from __future__ import annotations
from fleetos.agents.base import BaseAgent, AgentResult


class FinanceAgent(BaseAgent):
    name = "Finance"

    async def run(self, task: str, context: str) -> AgentResult:
        system = (
            "You are a financial modelling expert for early-stage internet businesses. "
            "Produce month-by-month revenue projections, cost breakdowns, and break-even "
            "analysis. Include key assumptions clearly. Format numbers clearly."
        )
        output = await self.call_llm(system, task)
        return AgentResult(role=self.name, output=output)
