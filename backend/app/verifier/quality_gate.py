import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class QualityGateEngine:
    """
    Quality Gate Engine
    Evaluates whether a problem package achieves the required 85/100 threshold before allowing export.
    Score breakdown:
    - Originality: 30
    - Clarity: 20
    - Correctness: 25
    - Test Coverage: 15
    - Educational Value: 10
    """
    THRESHOLD: float = 85.0

    @classmethod
    def evaluate(cls, score_data: Dict[str, Any]) -> Dict[str, Any]:
        total_score = score_data.get("total_score", 0.0)
        passes = total_score >= cls.THRESHOLD

        rejection_reasons = []
        if score_data.get("originality", 0) < 20.0:
            rejection_reasons.append("High similarity to existing problem corpus (Originality < 20/30)")
        if score_data.get("correctness", 0) < 20.0:
            rejection_reasons.append("Brute and optimal solutions failed differential verification (Correctness < 20/25)")
        if score_data.get("test_coverage", 0) < 10.0:
            rejection_reasons.append("Insufficient boundary or edge case test coverage (Coverage < 10/15)")

        return {
            "total_score": total_score,
            "pass_quality_gate": passes,
            "threshold": cls.THRESHOLD,
            "rejection_reasons": rejection_reasons,
            "can_export": passes
        }
