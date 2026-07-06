# 🌴 Vacation Copilot — Installation and Usage Guide

Welcome to **Vacation Copilot**, an elite, proactive travel concierge built on the **Google Agent Development Kit (ADK)** and managed via the unified `agents-cli` framework.

Vacation Copilot operates contextually across two distinct behavioral modes within a streamlined **Unified Flat Agent Architecture**:
1. **Onboarding Mode**: A conversational pre-trip intake interface where the agent interviews the traveler to extract travel dates, flight/hotel reservations, dietary restrictions, and planned activities.
2. **Live Trip Mode (On-the-ground)**: An active dining concierge that parses unstructured restaurant menus, cross-references them with the traveler's saved profile, and recommends optimized dishes with clear, safety-conscious reasoning.

---

## 📋 Table of Contents
1. [Prerequisites](#-prerequisites)
2. [Installation & Setup](#-installation--setup)
3. [Running the Agent Locally](#-running-the-agent-locally)
4. [Testing the Codebase](#-testing-the-codebase)
5. [Evaluation Loop (ADK Quality Flywheel)](#-evaluation-loop-adk-quality-flywheel)
6. [Deployment and Cloud Setup](#-deployment-and-cloud-setup)
7. [Project Architecture & Design](#-project-architecture--design)

---

## 🛠 Prerequisites

Before starting, ensure you have the following tools installed:

1. **Python (>=3.11, <3.14)**: The core codebase environment.
2. **uv**: A lightning-fast Python package and project environment manager.
   - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
3. **google-agents-cli**: The Agent Development Platform CLI.
   - Install using: `uv tool install google-agents-cli`
4. **Google Cloud SDK**: Required to authenticate and use Vertex AI / Gemini models in Google Cloud.
   - [Install Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

---

## 🚀 Installation & Setup

Follow these steps to set up the agent locally:

### 1. Authenticate with Google Cloud
Verify that you are logged into your Google Cloud account to enable authorized access to Gemini APIs:
```bash
# Log in to Google Cloud SDK
gcloud auth application-default login

# Log in to google-agents-cli
agents-cli login --interactive
```

### 2. Configure Environment Variables
Specify your Google Cloud project and location. Create a `.env` file in the project root directory (`vacation-copilot/`):
```bash
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
GOOGLE_CLOUD_LOCATION="us-east1" # or 'global'
```
*Note: The `.env` file is explicitly blocked by `.gitignore` to protect personal API credentials.*

### 3. Install Dependencies
Run the command below in the project root to provision the virtual environment and synchronize dependencies:
```bash
agents-cli install
```
This initializes `uv sync` under the hood, setting up the isolated environment and pinning lock files.

---

## 🖥 Running the Agent Locally

You can run and interact with the agent through multiple entry points:

### Method A: Web-based Playground (Recommended)
Open an interactive web interface to converse with Vacation Copilot and monitor execution traces:
```bash
agents-cli playground
```
This launches a local development server (typically on `http://localhost:8000`) with a chat layout showing the agent's internal reasoning steps and tool executions in real-time.

### Method B: Single-Prompt CLI Execution
Run a quick query straight from your terminal to verify agent responses:
```bash
agents-cli run "I want to see my itinerary"
```
To inspect tool parameters, state adjustments, and step metadata, add the verbose flag:
```bash
agents-cli run "Show my itinerary" -v
```

### Method C: FastAPI Server
The application is exposed as a production-ready FastAPI app. You can run it directly using uvicorn:
```bash
uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000
```
Once running, you can access the OpenAPI interactive documentation at `http://localhost:8000/docs`.

### 💡 Example Prompts to Test Behavioral Modes

Because the agent utilizes a flat architecture, it shifts behavior dynamically based on conversational context clues rather than delegating to sub-agents:

* **Testing Onboarding Mode**:
  * Prompt: *"Hi! Let's plan a trip to Paris next month."*
  * Prompt: *"Here is my hotel booking: Hotel Central, Paris, July 15-20."*
  * *Expected Behavior*: The agent interprets the travel intent, invokes `parse_travel_document`, updates the local markdown itinerary files, and contextually prompts for missing details (like flights or dietary profiles).
* **Testing Live Trip Mode**:
  * Prompt: *"Can you suggest gluten-free options from this menu? [Paste menu text here]"*
  * *Expected Behavior*: The agent evaluates the unstructured text against the user's dietary preferences, processes it via `parse_and_match_menu`, and yields safe recommendations.
* **Testing Direct Tools**:
  * Prompt: *"Show me my itinerary."*
  * *Expected Behavior*: The agent calls the `get_itinerary` tool directly within the loop to pull and present the current schedule details.

---

## 🧪 Testing the Codebase

Unit and integration tests are located in the `tests/` directory. They ensure the Python code, local tools, and file operations function correctly.

Run the test suite inside your virtual environment:
```bash
uv run pytest
```
*Note: Pytest suites verify infrastructure correctness (e.g., that file I/O works, types are valid). They do NOT assert on LLM output text. To validate non-deterministic conversational behavior, use the Evaluation Loop.*

---

## 📊 Evaluation Loop (ADK Quality Flywheel)

The `agents-cli` framework provides a powerful evaluation loop to benchmark the quality, safety, and correctness of your agent's responses.

### 1. Synthesize a Dataset
Generate a synthetic evaluation dataset tailored precisely to Vacation Copilot's use cases:
```bash
agents-cli eval dataset synthesize
```

### 2. Generate Traces
Run the agent over the evaluation dataset to capture complete conversational logs and execution traces:
```bash
agents-cli eval generate
```

### 3. Grade the Traces
Grade the compiled traces against the metrics configured in `eval_config.yaml`:
```bash
agents-cli eval grade
```

### 4. Run the Full Cycle
To execute generation and grading sequentially in a single action:
```bash
agents-cli eval run
```

### 5. Compare Performance & Check Regressions
When adjusting prompts or system guidelines, run a comparison check to ensure performance hasn't drifted:
```bash
agents-cli eval compare <base-run-results-json> <candidate-run-results-json>
```

---

## ☁️ Deployment and Cloud Setup

Vacation Copilot can be built and scaled seamlessly into production cloud architectures:

### Deploying the Application
To deploy the current version of the agent to Google Cloud:
```bash
# 1. Set your target project
gcloud config set project <your-project-id>

# 2. Deploy the agent
agents-cli deploy
```

### Enhancing Infrastructure
To upgrade to enterprise environments with full CI/CD automation pipelines (GitHub Actions/Cloud Build) and managed infrastructure as code:
```bash
agents-cli scaffold enhance .
```
Follow the interactive prompt to choose your target (e.g., **Cloud Run**), session state persistence layer, and repository CI/CD runners.

To set up the entire infrastructure pipeline:
```bash
agents-cli infra cicd
```

---

## 🏗 Project Architecture & Design

Vacation Copilot eliminates multi-agent routing bottlenecks by housing its execution logic in a flat, unified loop:

```
vacation-copilot/
├── app/
│   ├── agent.py                 # Core Unified Agent (root_agent)
│   ├── fast_api_app.py          # FastAPI application server wrapper
│   ├── tools/                   # Isolated business logic tools
│   │   ├── document_parser.py   # Extracts tokens from travel text strings
│   │   └── menu_analyzer.py     # Analyzes menus against profiles
│   └── shared/                  # Common utilities and data layer
│       └── markdown_store.py    # Local human-readable data storage engine
├── tests/                       # Automated test suites (unit + integration)
├── pyproject.toml               # Project dependencies and tool configurations
└── agents-cli-manifest.yaml     # Platform deployment manifest
```

- **Unified Core Agent (`root_agent`)**: The central execution node. It reads conversational context directly, selects specialized tools (`save_flight`, `parse_and_match_menu`), manages conversational tracking, and interacts with local human-readable storage files.
- **Tools**: Independent Python operations called deterministically by the agent loop depending on user intents.
- **Shared Data Layer**: Handles local, user-isolated sandbox storage, saving itineraries and profile parameters as clean, portable Markdown files.
```