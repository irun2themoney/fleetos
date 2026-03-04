"""Content Agent — writes copy, calendars, and email sequences."""

from __future__ import annotations
from fleetos.agents.base import BaseAgent, AgentResult


class ContentAgent(BaseAgent):
    name = "Content"

    async def run(self, task: str, context: str) -> AgentResult:
        system = (
            "You are an expert content strategist and copywriter. You produce "
            "high-converting, audience-specific content. Output structured content "
            "calendars, email sequences, and copy drafts with clear sections."
        )
        output = await self.call_llm(system, task)
        return AgentResult(role=self.name, output=output)
