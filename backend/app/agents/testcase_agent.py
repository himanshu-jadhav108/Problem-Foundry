import json
import logging
import random
from typing import Dict, Any, List
from app.providers.base import LLMProvider
from prompts.system_prompts import TESTCASE_AGENT_SYSTEM

logger = logging.getLogger(__name__)

class TestCaseAgent:
    """
    Independent Agent: TestCaseAgent
    Synthesizes boundary cases, edge cases, min/max limits, adversarial cases, and randomized stress tests.
    """
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def run(self, statement: Dict[str, Any], constraints: Dict[str, Any], num_cases: int = 10) -> List[Dict[str, Any]]:
        prompt = (
            f"Generate {num_cases} distinct competitive programming test cases for this problem:\n"
            f"Statement: {statement.get('formal_statement')}\n"
            f"Constraints: {json.dumps(constraints.get('constraints', []))}\n"
            f"Include boundary, edge, adversarial, and large random stress cases."
        )
        raw_response = await self.provider.generate(prompt, system=TESTCASE_AGENT_SYSTEM)
        try:
            cleaned = self._clean_json(raw_response)
            parsed = json.loads(cleaned)
            cases = parsed.get("test_cases", [])
            if cases:
                return cases
        except Exception as e:
            logger.warning(f"TestCaseAgent LLM generation fallback: {e}")

        # Algorithmic synthetic test generator fallback
        return self._generate_synthetic_cases(num_cases)

    def _generate_synthetic_cases(self, num_cases: int) -> List[Dict[str, Any]]:
        test_cases = [
            {
                "id": "tc_1_min_boundary",
                "input_data": "1\n42",
                "expected_output": "42",
                "is_hidden": False,
                "test_type": "boundary",
                "description": "Minimum boundary condition N = 1",
                "bug_detection_rank": 0.85
            },
            {
                "id": "tc_2_zero_elements",
                "input_data": "3\n0 0 0",
                "expected_output": "0",
                "is_hidden": False,
                "test_type": "edge",
                "description": "Zero element array handling",
                "bug_detection_rank": 0.90
            },
            {
                "id": "tc_3_negative_values",
                "input_data": "4\n-10 -20 30 40",
                "expected_output": "40",
                "is_hidden": True,
                "test_type": "adversarial",
                "description": "Negative numbers and sign flip boundary",
                "bug_detection_rank": 0.95
            }
        ]

        # Generate additional randomized stress cases to reach requested num_cases
        for i in range(4, num_cases + 1):
            n = random.randint(10, 100)
            arr = [random.randint(-1000, 1000) for _ in range(n)]
            test_cases.append({
                "id": f"tc_{i}_random_stress",
                "input_data": f"{n}\n" + " ".join(map(str, arr)),
                "expected_output": str(sum(arr)),
                "is_hidden": True,
                "test_type": "stress",
                "description": f"Randomized stress test with N={n}",
                "bug_detection_rank": 0.70
            })

        return test_cases

    def _clean_json(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
