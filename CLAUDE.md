# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                              # install/sync dependencies
uv run main.py                       # interactive CLI (one task per run, then exits)
uv run uvicorn app:app --reload      # API on http://127.0.0.1:8000
curl -X POST http://127.0.0.1:8000/build -H 'Content-Type: application/json' -d '{"prompt":"Build a Python calculator"}'
```

There is no test suite, no linter, and no formatter configured. To exercise a single
node in isolation, import it and hand it a `State` directly — every node takes and
returns state, so they run standalone:

```bash
uv run python -c "
from src.model.schema import State
from src.agents.coder import coder_node
print(coder_node(State(user_input='Build a CLI todo list')))"
```

Requires Docker running (the executor shells out to `docker run`) and a `.env` with
`OPENAI_API_KEY` and `OPENAI_MODEL_NAME`. `LANGSMITH_*` vars are optional tracing.

## Architecture

LangGraph agent that turns a plain-English request into a generated, executed, and
self-repaired Python project. Graph wiring lives in `src/graph.py`:

```
START → coder → writer → executor →(success)→ END
                            ↓ fail
                          critic →(pass)→ END
                                 →(retry_fix >= 5)→ END
                                 →(retry)→ coder
```

Things that only become clear by reading several files together:

- **`coder_node` has two modes keyed on `state.project is not None`.** First pass uses
  the full `ProjectOutput` schema; retries use the slim `FixOutput` schema so the LLM
  returns only the flagged files, which are merged by `file_path` into the existing
  file list. The retry counter `retry_fix` is incremented in the coder, not the critic.

- **The LLM's `project_directory` is never trusted.** Both `writer_node` and
  `executor_node` re-derive the real path as `GENERATED_PROJECTS_DIR / project_name`,
  reject names containing separators, and verify each resolved file path stays inside
  the project dir. The writer then overwrites `state.project.project_directory` with
  the trusted path. Keep that derivation intact when touching either node.

- **Node return types are inconsistent on purpose-by-accident.** `coder_node` and
  `critic_node` return partial-update dicts; `writer_node` and `executor_node` mutate
  and return the `State` object. That is why `main.py` and `app.py` both carry
  `_get`/`nested` helpers that read attributes from either a dict or a model — final
  state from `graph.invoke` may be either shape.

- **Each terminal command runs in its own fresh container** (`docker run --rm`, see
  `_docker_args`). Nothing survives between commands except the bind-mounted project
  directory. Networking is `none` by default, so generated code that tries to install
  or fetch anything will fail — which is why the coder prompt mandates stdlib-only.
  The container root filesystem is read-only, capabilities are dropped, and the mount
  uses `:Z` (SELinux) plus `--user $(id -u):$(id -g)` so generated code can still write
  its own JSON data files into the project mount.

- **Containers are named and killed on timeout.** `run_docker` gives each container a
  unique `phoenix-exec-*` name; on `TimeoutExpired` it runs `docker kill <name>`, because
  subprocess only kills the docker CLI and the container would otherwise keep running.

- **Generated programs must exit non-zero on fatal errors.** The coder prompt requires
  main.py's top-level handler to print to stderr and `sys.exit(1)`. Without that, a
  program that catches its own crash and exits 0 is judged a success and the critic
  never runs.

- **Success is not just the exit code.** `diagnose_error` also fails the run when
  stderr contains a traceback, `exception`, or `error:` — a program that exits 0 while
  printing an error line is still routed to the critic.

- **`file_inputs` becomes stdin for the first command only** (`_commands_with_inputs`),
  joined with newlines. Interactive generated programs are validated by scripted stdin,
  which is why the coder prompt requires every `input()` loop to have a deterministic
  exit value.

- **`settings` is a module-level singleton constructed at import time** and raises if
  `OPENAI_API_KEY` / `OPENAI_MODEL_NAME` are missing. Importing anything under `src/`
  therefore requires a populated `.env`.

- **`graph_builder()` is `lru_cache`d and has a side effect**: it writes `langgraph.png`
  via `draw_mermaid_png()` with default args, which calls the remote mermaid.ink API.
  Building the graph is not an offline operation. `app.py` calls `graph_builder()` per
  request, which the cache makes cheap after the first call.

## Conventions

- **Behavior of generated code is governed by prompts, not agent code.** Rules about
  project structure, stdlib-only dependencies, relative paths, JSON persistence, and
  the safety guardrails all live in `src/prompts/coder_prompt.py`. Change them there
  rather than post-processing output in `src/agents/`.
- Schemas in `src/model/schema.py` carry long `Field(description=...)` strings that are
  fed to the LLM as part of structured output — those descriptions are prompt surface,
  so edit them with the same care as the prompts.
- Every node and helper is wrapped in `@traceable` for LangSmith; keep new nodes traced.
- `generated_projects/` is gitignored except `accounts_manager/` and
  `library_management_system/`, which are deliberately tracked as portfolio samples.
