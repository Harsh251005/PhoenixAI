from pydantic import BaseModel, Field
from typing import Optional, List


class GeneratedFile(BaseModel):
    file_path: str = Field(
        description=(
            "Relative path of the file within the project, including subdirectories, "
            "using forward slashes only — e.g. 'calculator/add.py' or 'main.py'."
        )
    )
    file_description: str = Field(
        description=(
            "1-2 line description of this file's responsibility within the "
            "project — what it does, not how it's implemented."
        )
    )
    file_content: str = Field(
        description="Full, complete, runnable source code content of the file."
    )


class ProjectOutput(BaseModel):
    project_name: str = Field(
        description=(
            "A short, filesystem-safe folder name for this project in snake_case or "
            "kebab-case (e.g. 'expense_tracker_cli'), derived from the user's request. "
            "No spaces or special characters."
        )
    )
    project_directory: str = Field(
        description=(
            "The complete absolute path to the folder where this project's files were/will be "
            "generated (e.g. 'D:/Harsh/Code/generated_projects/expense_tracker_cli'). "
            "Should be the parent directory of file.file_path."
        )
    )
    description: str = Field(
        description=(
            "A 1-3 sentence plain-English summary of what the project does and who it's for, "
            "suitable for display in a project list or README header."
        )
    )
    files: List[GeneratedFile] = Field(
        description=(
            "The generated files for this project, including its path, name, full source code, "
            "and the stdin inputs required to execute and validate the main file."
        )
    )
    entry_point: str = Field(
        description=(
            "The main entry point for the project which should be executed by the subprocess."
            "Provide the complete path for the file"
        )
    )
    file_inputs: List[str] = Field(
        description=(
            "Concrete stdin values needed to run this program to completion via subprocess, "
            "in the exact order the program's input() calls will consume them. "
            "If the code contains ANY input() calls — including menu loops, REPLs, or "
            "prompts — you MUST provide a full realistic sequence of values that exercises "
            "the program (e.g. select a menu option, provide required data, then an exit "
            "command if the loop needs one to terminate). Only leave this empty if the code "
            "contains zero input() calls. Do not skip this because the program 'is interactive' "
            "— interactive programs still need scripted stdin to be validated."
        )
    )
    file_inputs_reason: str = Field(
        description=(
            "A line-by-line justification for each value in file_inputs, explaining which "
            "input() call it satisfies and why that value was chosen (e.g. 'Line 1: \"2\" "
            "selects menu option 2 (Add Expense)'). If file_inputs is empty, explicitly state "
            "why — e.g. 'No input() calls present in the code, so no stdin is required.' "
            "Never leave this blank."
        )
    )


class Errors(BaseModel):
    success: bool = Field(
        description=(
            "True only if this specific execution attempt ran to completion with exit code 0 "
            "and no unhandled exceptions or traceback in stderr. False for any crash, "
            "traceback, non-zero exit code, or hang that had to be killed."
        )
    )
    error_summary: str = Field(
        description=(
            "A concise, human-readable summary of what went wrong (e.g. exception type and "
            "message, such as 'TypeError: unsupported operand type(s) for +: int and str "
            "on line 42'). If success is True, state 'No errors' rather than leaving this vague."
        )
    )
    stdout: str = Field(
        description=(
            "The exact, unmodified standard output captured from running the program. "
            "Do not paraphrase or truncate meaningfully — preserve it as-is for debugging context."
        )
    )
    stderr: str = Field(
        description=(
            "The exact, unmodified standard error output (including full traceback if any) "
            "captured from running the program. Empty string if nothing was written to stderr."
        )
    )





class ExecutorResult(BaseModel):
    task: str = Field(
        description=(
            "The original user task/request that this code was generated to solve, copied "
            "verbatim or near-verbatim from the initial input so it can be logged alongside "
            "the execution outcome."
        )
    )
    file_path: str = Field(
        description=(
            "The absolute path on disk which the executor agent executed the code using subprocess "
            "(e.g. 'D:/Harsh/Code/generated_projects/expense_tracker_cli/main.py')."
        )
    )
    stdout: str = Field(
        description="The exact, unmodified standard output captured from running the file."
    )
    stderr: str = Field(
        description=(
            "The exact, unmodified standard error output (including full traceback, if any) "
            "captured from running the file. Empty string if execution produced no stderr."
        )
    )
    exit_code: int = Field(
        description=(
            "The process exit code returned by the subprocess. 0 indicates a clean, successful "
            "run; any non-zero value indicates a crash, unhandled exception, or explicit "
            "non-zero exit."
        )
    )
    success: bool = Field(
        description=(
            "True only if exit_code was 0 and stderr contains no traceback/exception — i.e. "
            "the program ran to completion as intended. False otherwise."
        )
    )
    error_summary: Optional[str] = Field(
        default=None,
        description=(
            "If success is False, the last/most relevant line of the traceback or error "
            "message (e.g. 'IndexError: list index out of range') to give quick, at-a-glance "
            "context without reading the full stderr. Leave as None when success is True."
        )
    )
    retry_count: int = Field(
        default=0,
        description=(
            "The number of retry attempts already made to fix and re-run this piece of code "
            "before this result. Starts at 0 for the first execution attempt and increments "
            "by 1 on each subsequent retry."
        )
    )


# Main Agent State
class State(BaseModel):
    user_input: str = Field(
        description=(
            "The original, unmodified request text from the user that kicks off the entire "
            "agent workflow (planner -> coder -> writer -> executor)."
        )
    )

    project: ProjectOutput | None = Field(
        default=None,
        description=(
            "The project generated by the planner/coder for this user_input, including the "
            "file contents and coder documentation. None until the coder node has produced "
            "an output."
        )
    )

    executor: ExecutorResult | None = Field(
        default=None,
        description=(
            "The result of executing project.file against project.file.file_inputs, including "
            "stdout/stderr and success status. None until the executor node has run."
        )
    )
