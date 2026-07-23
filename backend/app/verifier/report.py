import logging
from typing import List, Dict, Any
from app.verifier.comparator import ComparisonResult

logger = logging.getLogger(__name__)

class VerificationReportGenerator:
    """
    Verification Report Generator.
    Produces comprehensive, structured diagnostic verification reports.
    """

    @classmethod
    def generate_report(cls, results: List[ComparisonResult], problem_id: str = "prob_unknown") -> Dict[str, Any]:
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.is_match)
        failed_tests = total_tests - passed_tests
        
        nondeterministic_cases = sum(1 for r in results if r.is_nondeterministic)

        runtimes = [r.optimal_result.runtime_ms for r in results if r.optimal_result.runtime_ms > 0]
        avg_runtime = round(sum(runtimes) / max(1, len(runtimes)), 2) if runtimes else 0.0
        max_runtime = round(max(runtimes), 2) if runtimes else 0.0
        min_runtime = round(min(runtimes), 2) if runtimes else 0.0

        memories = [r.optimal_result.peak_memory_mb for r in results if r.optimal_result.peak_memory_mb > 0]
        avg_memory = round(sum(memories) / max(1, len(memories)), 2) if memories else 0.0

        detailed_failures = []
        for idx, r in enumerate(results, 1):
            if not r.is_match:
                detailed_failures.append({
                    "test_index": idx,
                    "reason": r.mismatch_reason,
                    "input_data": r.input_data,
                    "brute_output": r.brute_result.stdout,
                    "optimal_output": r.optimal_result.stdout,
                    "brute_stderr": r.brute_result.stderr,
                    "optimal_stderr": r.optimal_result.stderr,
                    "is_nondeterministic": r.is_nondeterministic
                })

        coverage_pct = round((passed_tests / max(1, total_tests)) * 100.0, 1)

        return {
            "problem_id": problem_id,
            "verification_status": "PASSED" if failed_tests == 0 and total_tests > 0 else "FAILED",
            "total_tests_run": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "nondeterministic_failures": nondeterministic_cases,
            "coverage_percentage": coverage_pct,
            "runtime_stats_ms": {
                "avg": avg_runtime,
                "min": min_runtime,
                "max": max_runtime
            },
            "memory_stats_mb": {
                "avg": avg_memory
            },
            "brute_vs_optimal_match": failed_tests == 0 and total_tests > 0,
            "detailed_failures": detailed_failures
        }
