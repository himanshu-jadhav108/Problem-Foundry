import logging
from typing import Dict, Any
from app.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class VerificationAgent:
    """
    Independent Agent: VerificationAgent
    Synthesizes execution verification results, testcase coverage, novelty scores, and statement clarity into the Quality Gate Score.
    """
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def run(
        self,
        novelty_report: Dict[str, Any],
        verification_report: Dict[str, Any],
        statement: Dict[str, Any],
        editorial: Dict[str, Any]
    ) -> Dict[str, Any]:
        # 1. Originality Score (Max 30)
        similarity = novelty_report.get("similarity_score", 0.2)
        originality = max(0.0, 30.0 * (1.0 - similarity))

        # 2. Clarity Score (Max 20)
        stmt_len = len(statement.get("formal_statement", ""))
        examples_count = len(statement.get("examples", []))
        clarity = 15.0
        if stmt_len > 50:
            clarity += 3.0
        if examples_count >= 1:
            clarity += 2.0
        clarity = min(20.0, clarity)

        # 3. Correctness Score (Max 25)
        if verification_report.get("brute_vs_optimal_match", False):
            correctness = 25.0
        else:
            total = max(1, verification_report.get("total_tests_run", 1))
            passed = verification_report.get("passed_tests", 0)
            correctness = round(25.0 * (passed / total), 1)

        # 4. Test Coverage Score (Max 15)
        cov = verification_report.get("coverage_percentage", 85.0)
        test_coverage = round(15.0 * (cov / 100.0), 1)

        # 5. Educational Value Score (Max 10)
        ed_pitfalls = len(editorial.get("common_pitfalls", []))
        educational_value = 8.0
        if ed_pitfalls >= 2:
            educational_value = 10.0

        total_score = round(originality + clarity + correctness + test_coverage + educational_value, 1)
        pass_quality_gate = total_score >= 85.0

        return {
            "originality": round(originality, 1),
            "clarity": round(clarity, 1),
            "correctness": round(correctness, 1),
            "test_coverage": round(test_coverage, 1),
            "educational_value": round(educational_value, 1),
            "total_score": total_score,
            "pass_quality_gate": pass_quality_gate
        }
