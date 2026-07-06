# 🌴 Vacation Copilot

Vacation Copilot is an elite, proactive travel concierge built on the **Google Agent Development Kit (ADK)** and managed via the `agents-cli` framework. 

By utilizing a high-performance **Unified Flat Agent Architecture**, a single core agent dynamically adapts its context window to manage two primary operational modes without the performance lag or context switching errors of traditional multi-agent supervisor systems.

## 🌟 Core Operational Modes

1. **Onboarding Mode (Pre-Trip Intake)**: A conversational interview layout where the agent collects travel dates, accommodation vouchers, flight information, and critical dietary needs.
2. **Live Trip Mode (On-the-Ground)**: An active dining safety concierge that takes unstructured restaurant menu text, runs safety validations against the traveler's saved profile, and returns concrete dish recommendations with distinct logic.

---

## 📂 Project Directory Structure

```
vacation-copilot/
├── app/                      # Core backend application layer
│   ├── agent.py              # Central Unified Agent configuration (root_agent)
│   ├── fast_api_app.py       # FastAPI application wrapper
│   ├── shared/               # Shared utilities (markdown data layer)
│   └── tools/                # Isolated functional Python tools
├── data/                     # Local isolated user storage sandboxes (auto-created)
├── tests/                    # Unit & integration test suites
├── GEMINI.md                  # AI-assisted development context guide
└── pyproject.toml            # Project dependencies and toolpins
```

---

## 🛠️ Prerequisites

Before getting started, make sure your local workspace has the following tools set up:
* **uv**: A lightning-fast Python package and project environment manager — [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
* **google-agents-cli**: The Agent Development Platform CLI. Install via: `uv tool install google-agents-cli`
* **Google Cloud SDK**: Required to authenticate your runtime against production Vertex AI / Gemini API endpoints — [Install GCloud SDK](https://cloud.google.com/sdk/docs/install)

---

## 🚀 Quick Start

### 1. Initialize the Environment
Install the global agents package components if you haven't already:
```bash
uvx google-agents-cli setup
```

### 2. Configure Environment Access
Authenticate your shell with your Google Cloud account credentials:
```bash
gcloud auth application-default login
agents-cli login --interactive
```
Create a `.env` file in your project root to export your targeted project parameters:
```bash
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
GOOGLE_CLOUD_LOCATION="us-east1"
```

## 📖 Detailed Developer Documentation
For a step-by-step breakdown of CLI configurations, interactive testing strategies, and the ADK Evaluation Flywheel, see the full [Installation and Usage Guide](docs/INSTRUCTIONS.md).


### 3. Synchronize Dependencies
Install the required system libraries and isolate your local virtual environment:
```bash
agents-cli install
```

### 4. Run the Local Playground
Launch the local development playground to interact with the agent in a web chat layout with real-time token tracking:
```bash
agents-cli playground
```

---

## 💻 CLI Command Index

| Command | Objective |
| :--- | :--- |
| **`agents-cli install`** | Syncs workspace dependencies using `uv` under the hood. |
| **`agents-cli playground`** | Launches an interactive local development UI at `http://localhost:8000`. |
| **`agents-cli run "query"`** | Runs a single execution turn straight inside your terminal (`-v` for verbose logs). |
| **`uv run pytest`** | Executes localized unit and structural integration tests. |
| **`agents-cli eval run`** | Triggers the complete ADK Flywheel (Dataset synthesis -> Trace generation -> Grading). |

---

## 🏗️ Production & Cloud Operations

| Utility Command | Operational Outcome |
| :--- | :--- |
| **`agents-cli deploy`** | Bundles and ships the unified agent straight to Google Cloud. |
| **`agents-cli scaffold enhance`** | Wireframes professional GitHub Actions/Cloud Build pipelines and Terraform infrastructure modules. |
| **`agents-cli infra cicd`** | Provision and deploy your entire production-grade enterprise runner infrastructure in one step. |

### 📈 Built-in Observability
Vacation Copilot includes out-of-the-box OpenTelemetry configurations. All tool executions, token metrics, and reasoning loops automatically export to **Cloud Trace**, **Cloud Logging**, and target **BigQuery** analytics tables for continuous evaluation.
```