import random
import logging
from typing import List, Dict, Any, Generator
try:
    from hypothesis import strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    st = None
    HAS_HYPOTHESIS = False

logger = logging.getLogger(__name__)

class HypothesisFuzzer:
    """
    Hypothesis-backed Fuzzer for competitive programming input synthesis.
    Generates diverse integer arrays, floating point values, matrices, and strings.
    """
    
    @classmethod
    def generate_array_inputs(cls, min_size: int = 1, max_size: int = 50, min_val: int = -1000, max_val: int = 1000, num_samples: int = 20) -> List[str]:
        """
        Generates formatted input strings: N on Line 1, array elements on Line 2.
        """
        inputs = []
        if HAS_HYPOTHESIS and st:
            strategy = st.lists(
                st.integers(min_value=min_val, max_value=max_val),
                min_size=min_size,
                max_size=max_size
            )
            for _ in range(num_samples):
                try:
                    arr = strategy.example()
                    input_str = f"{len(arr)}\n" + " ".join(map(str, arr))
                    inputs.append(input_str)
                except Exception:
                    n = random.randint(min_size, max_size)
                    arr = [random.randint(min_val, max_val) for _ in range(n)]
                    inputs.append(f"{n}\n" + " ".join(map(str, arr)))
        else:
            for _ in range(num_samples):
                n = random.randint(min_size, max_size)
                arr = [random.randint(min_val, max_val) for _ in range(n)]
                inputs.append(f"{n}\n" + " ".join(map(str, arr)))
        
        return inputs

    @classmethod
    def generate_matrix_inputs(cls, rows: int = 5, cols: int = 5, min_val: int = 0, max_val: int = 100) -> List[str]:
        """
        Generates 2D matrix formatted inputs.
        Line 1: R C
        Lines 2..R+1: C space-separated integers
        """
        inputs = []
        for _ in range(10):
            matrix = [[random.randint(min_val, max_val) for _ in range(cols)] for _ in range(rows)]
            lines = [f"{rows} {cols}"]
            for row in matrix:
                lines.append(" ".join(map(str, row)))
            inputs.append("\n".join(lines))
        return inputs

    @classmethod
    def generate_string_inputs(cls, min_len: int = 1, max_len: int = 100) -> List[str]:
        """
        Generates string inputs.
        """
        inputs = []
        for _ in range(10):
            length = random.randint(min_len, max_len)
            s = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length))
            inputs.append(f"{s}")
        return inputs
