import json
import logging
from typing import Dict, Any
from app.providers.base import LLMProvider
from prompts.system_prompts import EDITORIAL_AGENT_SYSTEM

logger = logging.getLogger(__name__)

class EditorialAgent:
    """
    Independent Agent: EditorialAgent
    Crafts comprehensive educational editorials with intuition, step-by-step walkthroughs, complexity proofs, and pitfall analysis.
    """
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def run(self, statement: Dict[str, Any], solution: Dict[str, Any], topic: str) -> Dict[str, Any]:
        prompt = (
            f"Write a deep educational editorial for this problem:\n"
            f"Statement: {statement.get('formal_statement')}\n"
            f"Topic: {topic}\n"
            f"Optimized Solution Complexity: {solution.get('optimized_complexity')}\n"
        )
        raw_response = await self.provider.generate(prompt, system=EDITORIAL_AGENT_SYSTEM)
        try:
            cleaned = self._clean_json(raw_response)
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"EditorialAgent JSON parsing failed: {e}")
            return {
                "intuition": f"The key intuition rests on observing the structural invariants of {topic}.",
                "step_by_step": "1. Parse input sequence.\n2. Maintain prefix aggregates or sliding window bounds.\n3. Compute target response efficiently.",
                "complexity_analysis": f"Time complexity is {solution.get('optimized_complexity', 'O(N)')}. Space complexity is O(N).",
                "common_pitfalls": [
                    "Failing to handle empty or N=1 array edge cases.",
                    "Overlooking 64-bit integer overflow bounds."
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
