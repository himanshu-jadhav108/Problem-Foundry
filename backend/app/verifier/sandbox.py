import sys
import subprocess
import tempfile
import os
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SandboxExecutionResult:
    def __init__(self, stdout: str, stderr: str, returncode: int, runtime_ms: float, timed_out: bool = False):
        self.stdout = stdout.strip()
        self.stderr = stderr.strip()
        self.returncode = returncode
        self.runtime_ms = runtime_ms
        self.timed_out = timed_out

    @property
    def is_success(self) -> bool:
        return self.returncode == 0 and not self.timed_out

class SubprocessSandbox:
    """
    Subprocess sandbox engine for executing Python reference code safely.
    Enforces per-test execution timeout and standard I/O isolation.
    """
    def __init__(self, timeout_seconds: float = 2.0):
        self.timeout_seconds = timeout_seconds

    def execute_python_code(self, code: str, input_data: str) -> SandboxExecutionResult:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as script_file:
            script_file.write(code)
            script_path = script_file.name

        start_time = time.perf_counter()
        try:
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=input_data, timeout=self.timeout_seconds)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return SandboxExecutionResult(
                stdout=stdout,
                stderr=stderr,
                returncode=process.returncode,
                runtime_ms=elapsed_ms,
                timed_out=False
            )
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            elapsed_ms = self.timeout_seconds * 1000.0
            return SandboxExecutionResult(
                stdout=stdout,
                stderr=stderr,
                returncode=-1,
                runtime_ms=elapsed_ms,
                timed_out=True
            )
        except Exception as e:
            logger.error(f"Sandbox execution exception: {e}")
            return SandboxExecutionResult(
                stdout="",
                stderr=str(e),
                returncode=1,
                runtime_ms=0.0,
                timed_out=False
            )
        finally:
            if os.path.exists(script_path):
                try:
                    os.remove(script_path)
                except OSError:
                    pass
