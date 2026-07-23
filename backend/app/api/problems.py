import uuid
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from app.schemas.problem import (
    ProblemGenerationRequest,
    GeneratedProblem,
    ProblemSolution,
    Editorial,
    TestCase,
    QualityScore,
    NoveltyReport,
    VerificationReport
)
from app.providers.factory import ProviderFactory
from app.agents import (
    IdeaAgent,
    StatementAgent,
    ConstraintAgent,
    SolutionAgent,
    EditorialAgent,
    TestCaseAgent,
    NoveltyAgent,
    VerificationAgent
)
from app.verifier.differential import DifferentialVerifier
from app.verifier.quality_gate import QualityGateEngine

router = APIRouter(prefix="/api/problems", tags=["Problems"])

@router.post("/generate", response_model=GeneratedProblem)
async def generate_problem(req: ProblemGenerationRequest):
    """
    Core Multi-Agent Generation Pipeline:
    Executes IdeaAgent -> StatementAgent -> ConstraintAgent -> SolutionAgent ->
    EditorialAgent -> TestCaseAgent -> NoveltyAgent -> VerificationAgent.
    """
    provider = ProviderFactory.get_provider()

    # 1. Idea Generation
    idea_agent = IdeaAgent(provider)
    idea = await idea_agent.run(req.topic, req.difficulty, req.target_complexity, req.educational_objective)

    # 2. Statement Synthesis
    stmt_agent = StatementAgent(provider)
    statement = await stmt_agent.run(idea, req.topic, req.difficulty)

    # 3. Constraint Formulation
    constraint_agent = ConstraintAgent(provider)
    constraints = await constraint_agent.run(statement, req.target_complexity)

    # 4. Solutions Generation (Brute + Optimal)
    sol_agent = SolutionAgent(provider)
    solution_data = await sol_agent.run(statement, constraints, req.target_complexity)
    solution = ProblemSolution(**solution_data)

    # 5. Editorial Synthesis
    ed_agent = EditorialAgent(provider)
    editorial_data = await ed_agent.run(statement, solution_data, req.topic)
    editorial = Editorial(**editorial_data)

    # 6. Test Case Synthesis
    tc_agent = TestCaseAgent(provider)
    raw_cases = await tc_agent.run(statement, constraints, num_cases=10)
    
    # 7. Differential Verification Execution
    verifier = DifferentialVerifier(timeout_seconds=2.0)
    verif_data = await verifier.verify_solutions(
        brute_code=solution.brute_force_code,
        optimized_code=solution.optimized_code,
        test_cases=raw_cases
    )
    verification_report = VerificationReport(**verif_data)

    # Fill expected output in test cases using optimal code execution
    formatted_public = []
    formatted_hidden = []
    for tc_dict in raw_cases:
        tc_obj = TestCase(**tc_dict)
        if tc_obj.is_hidden:
            formatted_hidden.append(tc_obj)
        else:
            formatted_public.append(tc_obj)

    # 8. Novelty Checker
    novelty_agent = NoveltyAgent(provider)
    novelty_data = await novelty_agent.run(statement.get("formal_statement", ""), idea.get("title", ""))
    novelty_report = NoveltyReport(**novelty_data)

    # 9. Quality Gate Scoring
    verif_agent = VerificationAgent(provider)
    quality_data = await verif_agent.run(
        novelty_report=novelty_data,
        verification_report=verif_data,
        statement=statement,
        editorial=editorial_data
    )
    quality_score = QualityScore(**quality_data)

    problem_id = f"prob_{uuid.uuid4().hex[:8]}"

    return GeneratedProblem(
        id=problem_id,
        title=idea.get("title", "Untitled Problem"),
        background=idea.get("background", ""),
        formal_statement=statement.get("formal_statement", ""),
        constraints=constraints.get("constraints", []),
        examples=statement.get("examples", []),
        solution=solution,
        editorial=editorial,
        public_test_cases=formatted_public,
        hidden_test_cases=formatted_hidden,
        metadata={
            "topic": req.topic,
            "difficulty": req.difficulty,
            "target_complexity": req.target_complexity,
            "educational_objective": req.educational_objective
        },
        quality_score=quality_score,
        novelty_report=novelty_report,
        verification_report=verification_report
    )

@router.post("/verify", response_model=VerificationReport)
async def verify_problem(payload: Dict[str, Any]):
    """
    Executes Python solution sandbox verification and differential fuzz testing.
    """
    brute_code = payload.get("brute_force_code", "")
    optimized_code = payload.get("optimized_code", "")
    test_cases = payload.get("test_cases", [])

    if not brute_code or not optimized_code:
        raise HTTPException(status_code=400, detail="Both brute_force_code and optimized_code are required.")

    verifier = DifferentialVerifier(timeout_seconds=2.0)
    verif_data = await verifier.verify_solutions(brute_code, optimized_code, test_cases)
    return VerificationReport(**verif_data)

@router.post("/novelty", response_model=NoveltyReport)
async def check_novelty(payload: Dict[str, Any]):
    """
    Evaluates problem novelty against local ChromaDB corpus.
    """
    formal_statement = payload.get("formal_statement", "")
    title = payload.get("title", "")
    provider = ProviderFactory.get_provider()
    agent = NoveltyAgent(provider)
    report = await agent.run(formal_statement, title)
    return NoveltyReport(**report)
