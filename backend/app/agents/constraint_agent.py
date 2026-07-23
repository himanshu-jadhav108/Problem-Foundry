import json
import logging
from typing import Dict, Any, List
from app.providers.base import LLMProvider
from prompts.system_prompts import CONSTRAINT_AGENT_SYSTEM

logger = logging.getLogger(__name__)

class ConstraintAgent:
    """
    Independent Agent: ConstraintAgent
    Formulates mathematical boundary constraints and target time/space execution bounds.
    """
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def run(self, statement: Dict[str, Any], target_complexity: str) -> Dict[str, Any]:
        prompt = (
            f"Formulate tight constraints and boundary conditions for this problem statement:\n"
            f"Statement: {statement.get('formal_statement')}\n"
            f"Target Complexity: {target_complexity}\n"
        )
        raw_response = await self.provider.generate(prompt, system=CONSTRAINT_AGENT_SYSTEM)
        try:
            cleaned = self._clean_json(raw_response)
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"ConstraintAgent JSON parsing failed: {e}")
            return {
                "constraints": [
                    "1 <= N <= 10^5",
                    "-10^9 <= A[i] <= 10^9",
                    "Time limit: 2.0 seconds",
                    "Memory limit: 512 MB"
                ],
                "boundary_notes": [
                    "Check N = 1 edge condition",
                    "Potential integer overflow requiring 64-bit integers"
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
