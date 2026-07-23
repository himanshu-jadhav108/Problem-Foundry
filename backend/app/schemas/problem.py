from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ProblemGenerationRequest(BaseModel):
    topic: str = Field(..., description="Algorithmic domain e.g. Dynamic Programming, Graph Algorithms, Segment Trees")
    difficulty: str = Field(..., description="Target difficulty level: Easy, Medium, Hard, Expert")
    target_complexity: str = Field(..., description="Expected time/space complexity e.g. O(N log N) time, O(N) space")
    educational_objective: str = Field(..., description="Key concept or trick to teach the problem solver")

class ExistingProblemTestCaseRequest(BaseModel):
    statement_or_url: str = Field(..., description="Full problem statement or problem URL metadata")
    num_cases: int = Field(default=20, ge=5, le=500, description="Number of testcases to generate")
    include_adversarial: bool = Field(default=True, description="Generate adversarial inputs targeting off-by-one and TLE")

class TestCase(BaseModel):
    __test__ = False
    id: str = Field(..., description="Unique testcase identifier")
    input_data: str = Field(..., description="Standard input string passed to solution execution")
    expected_output: str = Field(..., description="Expected stdout response")
    is_hidden: bool = Field(default=True, description="Whether this is a private submission test case")
    test_type: str = Field(default="randomized", description="boundary, edge, adversarial, stress, or example")
    description: Optional[str] = Field(default="", description="Description of targeted edge condition")
    bug_detection_rank: Optional[float] = Field(default=0.0, description="Bug detection capability score (0.0 to 1.0)")

class ProblemSolution(BaseModel):
    brute_force_code: str = Field(..., description="Python 3 naive/brute-force implementation")
    brute_force_complexity: str = Field(..., description="Big-O complexity of brute force solution")
    optimized_code: str = Field(..., description="Python 3 optimal reference implementation")
    optimized_complexity: str = Field(..., description="Big-O complexity of optimal solution")
    language: str = Field(default="python3", description="Programming language of reference code")

class Editorial(BaseModel):
    intuition: str = Field(..., description="Core intuition and key observations")
    step_by_step: str = Field(..., description="Detailed walkthrough of the algorithm")
    complexity_analysis: str = Field(..., description="Detailed proof of time and space complexity")
    common_pitfalls: List[str] = Field(default_factory=list, description="Common implementation traps and subtle bugs")

class QualityScore(BaseModel):
    originality: float = Field(..., ge=0, le=30, description="Score for novelty and freshness (max 30)")
    clarity: float = Field(..., ge=0, le=20, description="Score for statement readability and ambiguity avoidance (max 20)")
    correctness: float = Field(..., ge=0, le=25, description="Score for brute/optimal matching and execution validation (max 25)")
    test_coverage: float = Field(..., ge=0, le=15, description="Score for comprehensive edge case coverage (max 15)")
    educational_value: float = Field(..., ge=0, le=10, description="Score for pedagogical quality and editorial depth (max 10)")
    total_score: float = Field(..., ge=0, le=100, description="Overall sum score out of 100")
    pass_quality_gate: bool = Field(..., description="True if total_score >= 85")

class NoveltyReport(BaseModel):
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score against corpus (0 to 1)")
    duplicate_risk: str = Field(..., description="LOW, MEDIUM, HIGH risk level")
    matched_problems: List[Dict[str, Any]] = Field(default_factory=list, description="List of top similar problems from corpus")

class VerificationReport(BaseModel):
    total_tests_run: int = Field(..., description="Total differential tests executed")
    passed_tests: int = Field(..., description="Tests where brute and optimal outputs matched")
    failed_tests: int = Field(..., description="Mismatched or failed tests")
    runtime_ms: float = Field(..., description="Average optimal solution execution runtime in ms")
    memory_mb: float = Field(..., description="Peak memory consumption in MB")
    coverage_percentage: float = Field(..., description="Test case coverage percentage")
    brute_vs_optimal_match: bool = Field(..., description="Whether 100% of outputs matched")
    detailed_failures: List[Dict[str, Any]] = Field(default_factory=list, description="Log of mismatched inputs/outputs")

class GeneratedProblem(BaseModel):
    id: str = Field(..., description="UUID or problem slug identifier")
    title: str = Field(..., description="Problem title")
    background: str = Field(..., description="Problem motivation or lore context")
    formal_statement: str = Field(..., description="Rigorous mathematical and problem definition")
    constraints: List[str] = Field(..., description="Input size, bounds, and array element constraints")
    examples: List[Dict[str, str]] = Field(..., description="Sample inputs, outputs, and explanations")
    solution: ProblemSolution = Field(..., description="Brute-force and optimal code implementations")
    editorial: Editorial = Field(..., description="Complete educational editorial")
    public_test_cases: List[TestCase] = Field(default_factory=list, description="Visible sample test cases")
    hidden_test_cases: List[TestCase] = Field(default_factory=list, description="Hidden evaluation test cases")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Topic, difficulty, tags, author info")
    quality_score: Optional[QualityScore] = Field(default=None, description="Quality gate score breakdown")
    novelty_report: Optional[NoveltyReport] = Field(default=None, description="Novelty analysis output")
    verification_report: Optional[VerificationReport] = Field(default=None, description="Verification execution output")

class ModelSwitchRequest(BaseModel):
    provider_type: str = Field(..., description="ollama, openai_compatible, lmstudio, vllm")
    model_name: str = Field(..., description="Model identifier e.g. qwen2.5-coder:7b")
    api_base: str = Field(..., description="Local API base URL")
    api_key: Optional[str] = Field(default="", description="API key if required")
