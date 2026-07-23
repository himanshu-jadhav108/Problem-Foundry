import pytest
from app.schemas.testcase_analysis import ProblemAnalysisInput
from app.services.testcase_analyzer import TestCaseAnalyzerEngine, HISTORICAL_BUG_WEIGHTS
from app.providers.factory import ProviderFactory

@pytest.mark.asyncio
async def test_testcase_analyzer_identification_and_ranking():
    provider = ProviderFactory.get_provider()
    analyzer = TestCaseAnalyzerEngine(provider)

    input_data = ProblemAnalysisInput(
        statement="Given a graph with N nodes and M edges, find shortest path between node 1 and N.",
        constraints=["1 <= N <= 10^5", "1 <= M <= 2*10^5", "0 <= weight <= 10^9"],
        examples=[{"input": "3 2\n1 2 5\n2 3 10", "output": "15"}]
    )

    report = await analyzer.analyze_and_rank(input_data)

    assert report.problem_summary != ""
    assert "graph_corner_cases" in report.identified_risk_categories
    assert "overflow" in report.identified_risk_categories
    assert len(report.ranked_test_cases) > 0

    # Verify descending probability_score order
    scores = [tc.probability_score for tc in report.ranked_test_cases]
    assert scores == sorted(scores, reverse=True)

def test_historical_bug_weights_configuration():
    assert "off_by_one" in HISTORICAL_BUG_WEIGHTS
    assert HISTORICAL_BUG_WEIGHTS["off_by_one"] == 0.95
    assert HISTORICAL_BUG_WEIGHTS["overflow"] == 0.92
    assert HISTORICAL_BUG_WEIGHTS["binary_search_failure"] == 0.90
