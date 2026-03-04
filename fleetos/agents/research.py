"""Research Agent — competitor analysis, ICP profiling, keyword research."""

from __future__ import annotations
from fleetos.agents.base import BaseAgent, AgentResult


class ResearchAgent(BaseAgent):
    name = "Research"

    async def run(self, task: str, context: str) -> AgentResult:
        system = (
            "You are a market research analyst specialising in online business niches. "
            "Output structured research reports with competitor breakdowns, ICP profiles, "
            "keyword opportunities, and market sizing. Cite your reasoning clearly."
        )
        output = await self.call_llm(system, task)
        return AgentResult(role=self.name, output=output)
