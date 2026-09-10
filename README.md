# Phoenix AI

Phoenix AI is a LangGraph-powered code-generation agent. Give it a plain-English description of an application, and it generates a runnable project, writes the generated files to disk, executes the project, and uses a critic/coder retry loop when execution fails.

## How it works

The agent graph consists of four stages:

1. **Coder** — generates a project specification and complete source files using structured LLM output.
2. **Writer** — writes the generated files under `generated_projects/`.
3. **Executor** — runs the generated terminal commands and captures stdout, stderr, and the exit code.
4. **Critic** — evaluates failures and sends problematic files back to the coder for a maximum of five fix attempts.

Successful executions finish the graph. Failed executions are either retried or stopped after the retry limit is reached.

## Requirements

- Python 3.12 or newer
- [`uv`](https://docs.astral.sh/uv/)
- An OpenAI-compatible LLM configuration and, optionally, LangSmith tracing configuration as expected by `src/config/settings.py`

## Setup

Clone the repository and enter the project directory:

```bash
cd phoenix-ai
```

Create the local environment file expected by the project configuration and add the required LLM credentials. Do not commit this file:

```bash
touch .env
```

Install or synchronize dependencies:

```bash
uv sync
```

## Run the interactive CLI

Start Phoenix AI from the project root:

```bash
uv run main.py
```

Enter a request such as:

```text
Build a command-line expense tracker with add, list, and delete operations
```

Type `exit` to quit. Generated projects are written to:

```text
generated_projects/<project_name>/
```

The graph visualization is saved as `langgraph.png` when the graph is built.

## Run the FastAPI server

Start the development server with:

```bash
uv run uvicorn app:app --reload
```

The API is available at `http://127.0.0.1:8000`.

### Endpoints

#### `GET /`

Health-style endpoint:

```bash
curl http://127.0.0.1:8000/
```

#### `POST /build`

Generate and execute a project from a JSON request:

```bash
curl -X POST http://127.0.0.1:8000/build \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Build a Python calculator"}'
```

The response contains a concise project and execution summary rather than the complete internal agent state.

## Project structure

```text
phoenix-ai/
├── app.py                    # FastAPI application
├── main.py                   # Interactive CLI entry point
├── pyproject.toml            # Project metadata and dependencies
├── generated_projects/       # Generated applications
│   └── (executed through Docker by default)
└── src/
    ├── graph.py              # LangGraph workflow and routing
    ├── agents/
    │   ├── coder.py          # Initial generation and retry fixes
    │   ├── critic.py         # Execution-result evaluation
    │   ├── executor.py       # Subprocess execution and diagnostics
    │   └── writer.py         # Safe generated-file writing
    ├── model/schema.py       # Pydantic state and structured-output models
    ├── prompts/              # Coder and critic prompts
    └── config/               # Runtime settings
```

## Safety notes

- Generated file paths are checked to prevent writing outside the generated project directory.
- Generated code is executed in Docker with networking disabled by default, a read-only container root filesystem (the project mount itself stays writable so generated code can persist its own data files), dropped capabilities, non-root UID, and resource limits. Docker is not an absolute security boundary; review daemon and host configuration before treating it as a security control.
- Keep `.env` out of version control and never place credentials in generated project prompts or source files.

## Current limitations

- Generated projects are validated by executing the commands returned by the coder; validation quality depends on the generated commands and test inputs.
- There is no authentication or request queueing on the development API server.
