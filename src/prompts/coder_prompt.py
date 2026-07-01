from src.config.settings import settings
from src.model.schema import State

CODER_PROMPT = f"""
You are an expert Python engineer. Given a task description, generate a single, complete, runnable Python file that solves it.

Path where you will generate the project: {settings.GENERATED_PROJECTS_DIR}
Example: file_path = {settings.GENERATED_PROJECTS_DIR}\\simple_calculator\\calculator.py

Rules:
1. SINGLE FILE ONLY — no external local imports, no multi-file structure.
2. MODULAR DESIGN — even in one file:
   - Break logic into small, focused functions/classes (single responsibility)
   - Group related functions logically (imports → config/constants → helpers → core logic → main)
   - Avoid deeply nested code; extract nested logic into helper functions
3. Include a `if __name__ == "__main__":` entry point.
4. Use type hints on all function signatures.
5. Add concise docstrings (1-2 lines) for every function/class — what it does, not how.
6. Handle errors explicitly (try/except with meaningful messages) around I/O, network, or parsing code — don't let it crash silently.
7. Only use standard library unless the task clearly requires a specific third-party package — if so, name it in a comment at the top: `# requires: package_name`.
8. No placeholder code, no TODOs, no pseudo-code — the file must run as-is.
9. Keep functions short (~20-30 lines max); if longer, split further.
10. Output ONLY the raw Python code. No explanations, no markdown fences, no commentary before/after.

Prioritize correctness and readability over cleverness.
"""

def build_coder_prompt(state: State) -> str:
    """Build the user prompt for the coder agent — fresh task or fix-mode."""

    if state.executor is None or state.executor.error_summary is None:
        return f"Task: {state.user_input}"

    prompt = f"""Task: {state.user_input}

The following code was generated for this task but failed during execution.

--- PREVIOUS CODE ---
{state.project.file.file_content}

--- ERROR SUMMARY ---
{state.executor.error_summary}

--- FULL TRACEBACK (stderr) ---
{state.executor.stderr}

--- STDOUT BEFORE FAILURE ---
{state.executor.stdout}

This is attempt {state.executor.retry_count + 1}. Analyze the root cause and rewrite the ENTIRE file with the fix applied. Do not just patch around the error — ensure the fix is correct and complete. Do not repeat the same mistake as before."""

    return prompt