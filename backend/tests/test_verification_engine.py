import pytest
from app.verifier.sandbox import SubprocessSandbox
from app.verifier.fuzzer import HypothesisFuzzer
from app.verifier.comparator import OutputComparator
from app.verifier.report import VerificationReportGenerator

def test_sandbox_subprocess_execution():
    sandbox = SubprocessSandbox(timeout_seconds=2.0)
    code = "import sys\nprint(int(sys.stdin.read().strip()) * 2)\n"
    res = sandbox.execute_python_code(code, "21")
    assert res.is_success
    assert res.stdout == "42"

def test_sandbox_cpu_timeout():
    sandbox = SubprocessSandbox(timeout_seconds=0.5)
    infinite_loop_code = "import time\nwhile True:\n    time.sleep(0.1)\n"
    res = sandbox.execute_python_code(infinite_loop_code, "")
    assert res.timed_out
    assert not res.is_success

def test_hypothesis_fuzzer_array_generation():
    inputs = HypothesisFuzzer.generate_array_inputs(min_size=2, max_size=10, num_samples=5)
    assert len(inputs) == 5
    for inp in inputs:
        lines = inp.split("\n")
        assert len(lines) == 2
        n = int(lines[0])
        arr = list(map(int, lines[1].split()))
        assert len(arr) == n

def test_comparator_output_matching():
    sandbox = SubprocessSandbox(timeout_seconds=2.0)
    comparator = OutputComparator(sandbox)
    
    brute = "import sys\nprint(sum(map(int, sys.stdin.read().split()[1:])))\n"
    opt = "import sys\nprint(sum(map(int, sys.stdin.read().split()[1:])))\n"
    
    res = comparator.compare_single_case(brute, opt, "3\n10 20 30")
    assert res.is_match
    assert not res.is_nondeterministic

def test_comparator_output_mismatch_detection():
    sandbox = SubprocessSandbox(timeout_seconds=2.0)
    comparator = OutputComparator(sandbox)
    
    brute = "import sys\nprint(sum(map(int, sys.stdin.read().split()[1:])))\n"
    bugged_opt = "import sys\nprint(sum(map(int, sys.stdin.read().split()[1:])) + 1)\n" # Bugged off-by-one
    
    res = comparator.compare_single_case(brute, bugged_opt, "3\n10 20 30")
    assert not res.is_match
    assert "Output mismatch" in res.mismatch_reason

def test_comparator_nondeterminism_detection():
    sandbox = SubprocessSandbox(timeout_seconds=2.0)
    comparator = OutputComparator(sandbox)
    
    brute = "import sys\nprint(42)\n"
    nondeterministic_opt = "import sys, random\nprint(random.randint(1, 1000000))\n"
    
    res = comparator.compare_single_case(brute, nondeterministic_opt, "1\n5")
    assert not res.is_match
    assert res.is_nondeterministic
    assert "Nondeterminism detected" in res.mismatch_reason

def test_verification_report_generation():
    sandbox = SubprocessSandbox(timeout_seconds=2.0)
    comparator = OutputComparator(sandbox)
    
    brute = "import sys\nprint(sum(map(int, sys.stdin.read().split()[1:])))\n"
    opt = "import sys\nprint(sum(map(int, sys.stdin.read().split()[1:])))\n"
    
    c1 = comparator.compare_single_case(brute, opt, "2\n5 10")
    c2 = comparator.compare_single_case(brute, opt, "3\n1 2 3")
    
    report = VerificationReportGenerator.generate_report([c1, c2], problem_id="prob_test_123")
    assert report["verification_status"] == "PASSED"
    assert report["passed_tests"] == 2
    assert report["coverage_percentage"] == 100.0
    assert report["brute_vs_optimal_match"] is True
