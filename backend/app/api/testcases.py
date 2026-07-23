from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.schemas.problem import ExistingProblemTestCaseRequest, TestCase
from app.providers.factory import ProviderFactory
from app.agents import TestCaseAgent

router = APIRouter(prefix="/api/testcases", tags=["TestCases"])

@router.post("/generate", response_model=List[TestCase])
async def generate_testcases(req: ExistingProblemTestCaseRequest):
    """
    Generates tailored test cases for existing problems (pasted statements or metadata).
    Synthesizes boundary, edge, adversarial, and randomized stress cases.
    """
    provider = ProviderFactory.get_provider()
    agent = TestCaseAgent(provider)
    
    statement_dict = {"formal_statement": req.statement_or_url}
    constraints_dict = {"constraints": ["1 <= N <= 10^5"]}
    
    cases_data = await agent.run(statement_dict, constraints_dict, num_cases=req.num_cases)
    
    return [TestCase(**c) for c in cases_data]

@router.post("/rank", response_model=List[TestCase])
async def rank_testcases(cases: List[TestCase]):
    """
    Ranks test cases based on bug detection capability and boundary stress weight.
    """
    def compute_rank(tc: TestCase) -> float:
        score = 0.5
        if tc.test_type == "adversarial":
            score += 0.4
        elif tc.test_type == "boundary":
            score += 0.35
        elif tc.test_type == "edge":
            score += 0.3
        elif tc.test_type == "stress":
            score += 0.2
        return min(1.0, round(score, 2))

    for tc in cases:
        tc.bug_detection_rank = compute_rank(tc)

    # Sort descending by bug_detection_rank
    cases.sort(key=lambda x: x.bug_detection_rank or 0.0, reverse=True)
    return cases
