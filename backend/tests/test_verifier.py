import pytest
from app.verifier.sandbox import SubprocessSandbox
from app.verifier.differential import DifferentialVerifier
from app.verifier.quality_gate import QualityGateEngine
from app.schemas.problem import ProblemGenerationRequest, TestCase

def test_sandbox_execution_success():
    sandbox = SubprocessSandbox(timeout_seconds=2.0)
    code = (
        "import sys\n"
        "data = sys.stdin.read().strip()\n"
        "print(f'Echo: {data}')\n"
    )
    res = sandbox.execute_python_code(code, "Hello Foundry")
    assert res.is_success
    assert res.stdout == "Echo: Hello Foundry"
    assert res.runtime_ms > 0

def test_sandbox_timeout_trapping():
    sandbox = SubprocessSandbox(timeout_seconds=0.5)
    infinite_loop_code = "import time\ntime.sleep(5)\n"
    res = sandbox.execute_python_code(infinite_loop_code, "")
    assert res.timed_out
    assert not res.is_success

@pytest.mark.asyncio
async def test_differential_verifier_matching():
    verifier = DifferentialVerifier(timeout_seconds=2.0)
    brute_code = (
        "import sys\n"
        "nums = list(map(int, sys.stdin.read().split()))\n"
        "print(sum(nums))\n"
    )
    opt_code = (
        "import sys\n"
        "nums = list(map(int, sys.stdin.read().split()))\n"
        "total = 0\n"
        "for x in nums:\n"
        "    total += x\n"
        "print(total)\n"
    )
    test_cases = [
        {"id": "tc1", "input_data": "1 2 3 4 5", "expected_output": "15"},
        {"id": "tc2", "input_data": "100 -50 25", "expected_output": "75"}
    ]
    report = await verifier.verify_solutions(brute_code, opt_code, test_cases)
    assert report["passed_tests"] == 2
    assert report["failed_tests"] == 0
    assert report["brute_vs_optimal_match"] is True

def test_quality_gate_threshold_rejection():
    failing_score = {
        "originality": 15.0,
        "clarity": 15.0,
        "correctness": 20.0,
        "test_coverage": 10.0,
        "educational_value": 8.0,
        "total_score": 68.0
    }
    result = QualityGateEngine.evaluate(failing_score)
    assert result["pass_quality_gate"] is False
    assert result["can_export"] is False
    assert len(result["rejection_reasons"]) > 0

def test_quality_gate_threshold_pass():
    passing_score = {
        "originality": 28.0,
        "clarity": 19.0,
        "correctness": 25.0,
        "test_coverage": 14.0,
        "educational_value": 9.0,
        "total_score": 95.0
    }
    result = QualityGateEngine.evaluate(passing_score)
    assert result["pass_quality_gate"] is True
    assert result["can_export"] is True
