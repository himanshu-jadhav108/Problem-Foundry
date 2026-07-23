import json
import logging
from typing import Dict, Any
from app.providers.base import LLMProvider
from prompts.system_prompts import IDEA_AGENT_SYSTEM

logger = logging.getLogger(__name__)

class IdeaAgent:
    """
    Independent Agent: IdeaAgent
    Transforms topic, difficulty, target complexity, and educational objectives into high-level problem concepts.
    """
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def run(self, topic: str, difficulty: str, target_complexity: str, educational_objective: str) -> Dict[str, Any]:
        prompt = (
            f"Generate a novel problem idea with these specifications:\n"
            f"Topic: {topic}\n"
            f"Difficulty: {difficulty}\n"
            f"Target Complexity: {target_complexity}\n"
            f"Educational Objective: {educational_objective}\n"
        )
        raw_response = await self.provider.generate(prompt, system=IDEA_AGENT_SYSTEM)
        try:
            # Clean JSON markdown blocks if model returns ```json ... ```
            cleaned = self._clean_json(raw_response)
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"IdeaAgent JSON parsing failed, using fallback parser: {e}")
            return {
                "title": f"Original {topic} Challenge: {educational_objective[:30]}",
                "background": f"In a high-throughput computational system, you are tasked with solving a {difficulty.lower()} problem involving {topic}.",
                "core_idea": f"Leverage {topic} principles to achieve {target_complexity}.",
                "math_concept": educational_objective
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
