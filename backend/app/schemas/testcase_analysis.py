from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ProblemAnalysisInput(BaseModel):
    statement: str = Field(..., description="Problem description or formal statement")
    constraints: List[str] = Field(default_factory=list, description="Problem constraints e.g. 1 <= N <= 10^5")
    examples: List[Dict[str, str]] = Field(default_factory=list, description="Sample inputs and outputs")

class HighValueTestCase(BaseModel):
    __test__ = False
    id: str = Field(..., description="Testcase identifier")
    input_data: str = Field(..., description="Formatted input data string")
    expected_output: str = Field(..., description="Expected output string")
    bug_category: str = Field(..., description="One of 10 bug risk categories e.g. off_by_one, overflow, binary_search_failure")
    probability_score: float = Field(..., ge=0.0, le=1.0, description="Probability score of catching incorrect solutions (0.0 to 1.0)")
    explanation: str = Field(..., description="Detailed explanation of targeted vulnerability")
    historical_bug_weight: float = Field(default=1.0, description="Weight multiplier derived from historical bug patterns")

class AnalysisReport(BaseModel):
    problem_summary: str = Field(..., description="Identified problem domain and risk profile")
    identified_risk_categories: List[str] = Field(..., description="List of detected risk categories")
    ranked_test_cases: List[HighValueTestCase] = Field(..., description="Test cases ranked descending by probability_score")
