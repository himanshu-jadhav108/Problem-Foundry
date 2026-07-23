import logging
from typing import Dict, Any, List, Tuple
from app.verifier.sandbox import SubprocessSandbox, SandboxExecutionResult

logger = logging.getLogger(__name__)

class ComparisonResult:
    def __init__(
        self,
        input_data: str,
        brute_result: SandboxExecutionResult,
        optimal_result: SandboxExecutionResult,
        is_match: bool,
        is_nondeterministic: bool = False,
        mismatch_reason: str = ""
    ):
        self.input_data = input_data
        self.brute_result = brute_result
        self.optimal_result = optimal_result
        self.is_match = is_match
        self.is_nondeterministic = is_nondeterministic
        self.mismatch_reason = mismatch_reason

class OutputComparator:
    """
    Output Comparator & Nondeterminism Detector.
    Compares outputs of brute-force vs. optimal solutions and validates determinism.
    """
    def __init__(self, sandbox: SubprocessSandbox):
        self.sandbox = sandbox

    def compare_single_case(
        self,
        brute_code: str,
        optimized_code: str,
        input_data: str,
        nondeterminism_checks: int = 3
    ) -> ComparisonResult:
        """
        Executes brute and optimal solution on input_data.
        Checks for output matching and verifies nondeterminism by running optimal code multiple times.
        """
        # Execute brute force once
        brute_res = self.sandbox.execute_python_code(brute_code, input_data)
        
        # Execute optimal solution first time
        opt_res_initial = self.sandbox.execute_python_code(optimized_code, input_data)

        if not opt_res_initial.is_success:
            return ComparisonResult(
                input_data=input_data,
                brute_result=brute_res,
                optimal_result=opt_res_initial,
                is_match=False,
                is_nondeterministic=False,
                mismatch_reason=f"Optimal execution failed (Error: {opt_res_initial.stderr or 'Timeout'})"
            )

        if not brute_res.is_success:
            return ComparisonResult(
                input_data=input_data,
                brute_result=brute_res,
                optimal_result=opt_res_initial,
                is_match=False,
                is_nondeterministic=False,
                mismatch_reason=f"Brute-force execution failed (Error: {brute_res.stderr or 'Timeout'})"
            )

        # Output matching check (normalized whitespace)
        brute_clean = self._normalize_output(brute_res.stdout)
        opt_clean = self._normalize_output(opt_res_initial.stdout)
        is_match = (brute_clean == opt_clean)

        mismatch_reason = ""
        if not is_match:
            mismatch_reason = f"Output mismatch: brute output '{brute_clean}' != optimal output '{opt_clean}'"

        # Nondeterminism verification: Execute optimal solution multiple times
        is_nondeterministic = False
        for _ in range(nondeterminism_checks - 1):
            subsequent_res = self.sandbox.execute_python_code(optimized_code, input_data)
            subsequent_clean = self._normalize_output(subsequent_res.stdout)
            if subsequent_clean != opt_clean:
                is_nondeterministic = True
                mismatch_reason = f"Nondeterminism detected! Run 1 output: '{opt_clean}', Run 2 output: '{subsequent_clean}'"
                break

        return ComparisonResult(
            input_data=input_data,
            brute_result=brute_res,
            optimal_result=opt_res_initial,
            is_match=is_match and not is_nondeterministic,
            is_nondeterministic=is_nondeterministic,
            mismatch_reason=mismatch_reason
        )

    def _normalize_output(self, stdout: str) -> str:
        lines = [line.strip() for line in stdout.strip().splitlines()]
        return "\n".join(lines)
