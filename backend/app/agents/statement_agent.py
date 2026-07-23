import json
import logging
from typing import Dict, Any
from app.providers.base import LLMProvider
from prompts.system_prompts import STATEMENT_AGENT_SYSTEM

logger = logging.getLogger(__name__)

class StatementAgent:
    """
    Independent Agent: StatementAgent
    Drafts rigorous formal problem statements, input/output formats, and worked examples with explanations.
    """
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def run(self, idea: Dict[str, Any], topic: str, difficulty: str) -> Dict[str, Any]:
        prompt = (
            f"Write a formal problem statement for the following problem concept:\n"
            f"Title: {idea.get('title')}\n"
            f"Background: {idea.get('background')}\n"
            f"Core Idea: {idea.get('core_idea')}\n"
            f"Topic: {topic}\n"
            f"Difficulty: {difficulty}\n"
        )
        raw_response = await self.provider.generate(prompt, system=STATEMENT_AGENT_SYSTEM)
        try:
            cleaned = self._clean_json(raw_response)
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"StatementAgent JSON parsing failed: {e}")
            return {
                "formal_statement": f"Given an integer N and an array A of N integers, find the optimal subset satisfying the {topic} condition.",
                "input_format": "The first line contains an integer N. The second line contains N space-separated integers.",
                "output_format": "Print a single integer representing the optimal answer.",
                "examples": [
                    {
                        "input": "5\n1 2 3 4 5",
                        "output": "15",
                        "explanation": "Sum of all elements is 15."
                    }
                ]
            }

    def _clean_json(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
