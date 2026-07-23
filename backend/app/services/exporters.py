import json
import io
import zipfile
import logging
from typing import Dict, Any
from app.schemas.problem import GeneratedProblem

logger = logging.getLogger(__name__)

class ExportService:
    """
    Exporters for problem packages: Markdown, JSON, LeetCode-style zip package, and PDF-ready Markdown.
    """

    @classmethod
    def to_markdown(cls, problem: GeneratedProblem) -> str:
        md = []
        md.append(f"# {problem.title}\n")
        md.append(f"**Topic**: {problem.metadata.get('topic', 'Algorithms')} | **Difficulty**: {problem.metadata.get('difficulty', 'Medium')} | **Target Complexity**: {problem.metadata.get('target_complexity', 'O(N)')}\n")
        md.append("## Background\n")
        md.append(f"{problem.background}\n")
        md.append("## Problem Statement\n")
        md.append(f"{problem.formal_statement}\n")
        
        md.append("## Constraints\n")
        for c in problem.constraints:
            md.append(f"- `{c}`")
        md.append("\n")

        md.append("## Examples\n")
        for i, ex in enumerate(problem.examples, 1):
            md.append(f"### Example {i}\n")
            md.append(f"**Input:**\n```\n{ex.get('input', '')}\n```\n")
            md.append(f"**Output:**\n```\n{ex.get('output', '')}\n```\n")
            if ex.get('explanation'):
                md.append(f"**Explanation:** {ex.get('explanation')}\n")

        md.append("## Optimal Reference Solution (Python 3)\n")
        md.append(f"```python\n{problem.solution.optimized_code}\n```\n")
        md.append(f"**Complexity:** {problem.solution.optimized_complexity}\n")

        md.append("## Editorial\n")
        md.append(f"### Intuition\n{problem.editorial.intuition}\n")
        md.append(f"### Walkthrough\n{problem.editorial.step_by_step}\n")
        md.append(f"### Complexity Analysis\n{problem.editorial.complexity_analysis}\n")
        if problem.editorial.common_pitfalls:
            md.append("### Common Pitfalls\n")
            for pitfall in problem.editorial.common_pitfalls:
                md.append(f"- {pitfall}")
            md.append("\n")

        if problem.quality_score:
            md.append("## Quality Score Breakdown\n")
            md.append(f"- **Total Score**: {problem.quality_score.total_score} / 100")
            md.append(f"- **Originality**: {problem.quality_score.originality} / 30")
            md.append(f"- **Clarity**: {problem.quality_score.clarity} / 20")
            md.append(f"- **Correctness**: {problem.quality_score.correctness} / 25")
            md.append(f"- **Test Coverage**: {problem.quality_score.test_coverage} / 15")
            md.append(f"- **Educational Value**: {problem.quality_score.educational_value} / 10\n")

        return "\n".join(md)

    @classmethod
    def to_json(cls, problem: GeneratedProblem) -> str:
        return problem.model_dump_json(indent=2)

    @classmethod
    def to_leetcode_package(cls, problem: GeneratedProblem) -> bytes:
        """
        Generates a standard zip archive containing problem.md, solution.py, testcases.txt, and metadata.json.
        """
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add problem statement
            zf.writestr("problem.md", cls.to_markdown(problem))
            # Add optimal solution code
            zf.writestr("solution.py", problem.solution.optimized_code)
            # Add brute force solution code
            zf.writestr("solution_brute.py", problem.solution.brute_force_code)
            
            # Format testcases
            testcase_str = []
            for tc in problem.public_test_cases + problem.hidden_test_cases:
                testcase_str.append(f"=== TESTCASE {tc.id} ({tc.test_type}) ===")
                testcase_str.append("--- INPUT ---")
                testcase_str.append(tc.input_data)
                testcase_str.append("--- EXPECTED ---")
                testcase_str.append(tc.expected_output)
                testcase_str.append("")
            zf.writestr("testcases.txt", "\n".join(testcase_str))
            
            # Metadata
            zf.writestr("metadata.json", cls.to_json(problem))

        return buffer.getvalue()

    @classmethod
    def to_pdf_ready_markdown(cls, problem: GeneratedProblem) -> str:
        base_md = cls.to_markdown(problem)
        pdf_header = (
            "<style>\n"
            "body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }\n"
            "h1 { color: #1e293b; border-bottom: 2px solid #3b82f6; padding-bottom: 8px; }\n"
            "pre { background: #f1f5f9; padding: 12px; border-radius: 6px; overflow-x: auto; }\n"
            "code { font-family: monospace; background: #e2e8f0; padding: 2px 4px; border-radius: 4px; }\n"
            "</style>\n\n"
        )
        return pdf_header + base_md
