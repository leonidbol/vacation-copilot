# Coding Agent Guide

## Prerequisites

Install the CLI (one-time):
```bash
uv tool install google-agents-cli
```

---

## Development Phases

### Phase 1: Understand Requirements
Before writing any code, thoroughly review the project's requirements, architectural patterns, safety rules, and success criteria specified in `.agents-cli-spec.md`.

### Phase 2: Build and Implement
Implement agent logic inside the `app/` directory. Use `agents-cli playground` for interactive local manual testing and iterate directly based on immediate execution behaviors.

### Phase 3: The Evaluation Loop (Main Iteration Phase)
Start with 1–2 evaluation cases, run `agents-cli eval generate`, and then run `agents-cli eval grade`. Continually iterate on your prompts and logic, rerunning both commands until behavior converges safely. Expect 5–10+ iterations. Once you establish a stable baseline, leverage advanced tooling surfaces:
- `agents-cli eval compare` — Check for regression deltas across candidate runs.
- `agents-cli eval analyze` — Automatically cluster failure modes from grader outputs.
- `agents-cli eval optimize` — Auto-tune agent prompts using compiled evaluation sets.

### Phase 4: Pre-Deployment Tests
Execute the local regression test suite: `uv run pytest tests/unit tests/integration`. Resolve all infrastructure, validation, and mocking issues until the entire pipeline passes with zero errors.

### Phase 5: Deploy to Dev
**Requires explicit human approval.** Run `agents-cli deploy` only after the user confirms they are ready to publish the dev tracking layer.

### Phase 6: Production Deployment
Coordinate with the user to select the appropriate production delivery channel: **Option A** (simple single-project architecture) or **Option B** (full CI/CD GitOps automation pipeline utilizing `agents-cli infra cicd`).

---

## Development Commands

| Command | Purpose |
| :--- | :--- |
| `agents-cli playground` | Launches an interactive local chat UI for diagnostic testing. |
| `uv run pytest tests/unit tests/integration` | Executes offline unit tests and live integration suites. |
| `agents-cli eval dataset synthesize` | Synthesizes synthetic multi-turn evaluation datasets for scenarios. |
| `agents-cli eval generate` | Runs the agent against an evaluation dataset to emit execution traces. |
| `agents-cli eval grade` | Evaluates emitted execution traces against specific SDK metrics. |
| `agents-cli eval compare` | Diff-checks two separate grading results to track behavioral regression. |
| `agents-cli eval analyze` | Clusters and categorizes structural failure modes from test results. |
| `agents-cli eval metric list` | Lists all built-in LLM-as-a-judge metrics available in the SDK. |
| `agents-cli eval optimize` | Automatically tunes and optimizes agent system prompts. |
| `agents-cli lint` | Runs statutory code quality, formatting, and typing checks. |
| `agents-cli infra single-project` | Sets up target GCP cloud infrastructure via compiled Terraform. |
| `agents-cli deploy` | Builds, packages, and deploys the agent application state to dev. |
| `agents-cli scaffold enhance` | Enhances an existing footprint with new deployment configurations. |
| `agents-cli scaffold upgrade` | Upgrades current boilerplate files to match the latest SDK layout. |

---

## Operational Guidelines for Coding Agents

- **Code Preservation**: Only modify code blocks directly targeted by the user's explicit request. Preserve all surrounding code, configuration properties, architectural styles, comments, and spacing conventions.
- **Architecture Integrity**: Respect the project's streamlined **Unified Flat Agent Architecture**. Do not fragment the application context by splitting logic back into sub-agents or complex orchestration charts unless explicitly instructed.
- **Model Lock**: Never change the underlying Gemini model variants or naming keys unless explicitly commanded to do so.
- **Model 404 Errors**: If a regional model error occurs, fix the target environment location variable (`GOOGLE_CLOUD_LOCATION` to an active region like `global` or `us-east1`) rather than rewriting the core model identifier strings.
- **ADK Tool Imports**: Import the explicit tool execution instance directly rather than importing its parent module wrapper. For example:  
  `from google.adk.tools.load_web_page import load_web_page`
- **Isolated Execution Environment**: Always run Python scripts using the `uv` toolchain to guarantee lockfile isolation: `uv run python script.py`. Ensure `agents-cli install` runs first on new initialization paths.
- **Circuit Breaker on Repetition**: If an execution, linting, or evaluation error manifests 3+ times consecutively, halt iterations immediately. Analyze the system logs to fix the systemic root cause instead of blindly repeating modifications.
- **Terraform Resource Conflicts (Error 409)**: If infrastructure provisioning returns resource conflicts, use `terraform import` targets to bring existing state under management rather than forcing dirty recreation loops.