# Problem Foundry 🚀
> Model-Agnostic Local AI System for Algorithmic Problem Authoring, Differential Verification, and Test Case Synthesis.

Problem Foundry is a fully local AI engineering platform designed to assist competitive programming authors, educators, and contest designers in creating original LeetCode-style problems, verifying solution correctness using differential fuzz testing, analyzing problem novelty against a vector database, and generating contestant-ready export packages.

---

## 🌟 Key Features

1. **Fully Local & Cloud-Independent**: Zero cloud API dependencies. Runs on local LLM runtimes (Ollama, LM Studio, vLLM, LocalAI).
2. **Model-Agnostic Provider Layer**: Switch between models dynamically (`qwen2.5-coder`, `llama3.1`, `deepseek-r1`) via single config or API endpoint.
3. **8-Agent Autonomous Architecture**:
   - `IdeaAgent`: Generates underlying mathematical and algorithmic problem concepts.
   - `StatementAgent`: Formulates clear, unambiguous problem statements and sample IO.
   - `ConstraintAgent`: Formulates tight time/space complexity bounds ($N \le 10^5$, 2.0s limit).
   - `SolutionAgent`: Synthesizes both Python brute-force ($O(N^2)$) and optimal ($O(N \log N)$ or $O(N)$) reference code.
   - `EditorialAgent`: Crafts deep educational tutorials, step-by-step walkthroughs, and pitfall analysis.
   - `TestCaseAgent`: Generates boundary cases, min/max limits, adversarial inputs, and stress tests.
   - `NoveltyAgent`: Embeds problem statements via ChromaDB to evaluate novelty and duplicate risk.
   - `VerificationAgent`: Aggregates Quality Gate metrics across 5 dimensions.
4. **Subprocess Sandbox & Differential Verification Engine**: Runs reference Python solutions in isolated subprocess sandboxes with per-test memory/CPU execution timeouts and compares brute-force vs. optimal outputs across 10,000 randomized test cases.
5. **Quality Gate Gatekeeper**: Evaluates total quality score (Originality 30, Clarity 20, Correctness 25, Test coverage 15, Educational value 10). Rejects package exports unless total score $\ge 85 / 100$.
6. **Multi-Format Contest Exporter**: Generates Markdown, JSON, PDF-ready HTML, and LeetCode-style Zip packages containing `problem.md`, `solution.py`, `solution_brute.py`, and `testcases.txt`.

---

## 🏗️ System Architecture & Folder Structure

```
problem-foundry/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers (/problems, /testcases, /models)
│   │   ├── agents/       # 8 independent multi-agent Python classes
│   │   ├── providers/    # LLMProvider abstraction (Ollama, OpenAI-compatible)
│   │   ├── verifier/     # Subprocess sandbox & differential verifier engine
│   │   ├── services/     # Package export engine (Markdown, JSON, Zip)
│   │   ├── models/       # SQLAlchemy database models (Postgres / SQLite)
│   │   ├── schemas/      # Pydantic v2 data transfer objects
│   │   └── main.py       # FastAPI application entry point
│   ├── tests/            # Pytest execution and verification tests
│   ├── requirements.txt  # Python 3.12 dependencies
│   └── .env.example      # Local environment configuration
├── frontend/             # Next.js 15 / React 19 / Tailwind CSS UI dashboard
├── prompts/              # System prompt templates for 8 agents
├── examples/             # Sample generated problem JSON packages
├── docs/                 # Operational manuals and API specifications
└── docker-compose.yml    # Docker container deployment setup
```

---

## ⚡ Environment & Local Model Setup

### 1. Ollama Setup Commands

Install and serve local models using Ollama:

```bash
# 1. Install Ollama (Windows / macOS / Linux)
# Download installer from https://ollama.com

# 2. Pull target coding and reasoning models
ollama pull qwen2.5-coder:7b
ollama pull llama3.1:8b

# 3. Start local Ollama server (Runs at http://localhost:11434)
ollama serve
```

### 2. LM Studio / vLLM Setup Commands

For LM Studio or vLLM:
- **LM Studio**: Open Local Server tab, select model, set port `1234`, and click "Start Server".
- **vLLM**: Run `vllm serve Qwen/Qwen2.5-Coder-7B-Instruct --port 8000`

---

## 🛠️ Installation & Running Locally

### Option A: Local Python & Node Execution

#### Step 1: Backend Setup
```bash
cd backend
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Linux / macOS:
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

# Run FastAPI backend
uvicorn app.main:app --reload --port 8080
```
Backend API will be live at `http://localhost:8080` (Swagger UI at `http://localhost:8080/docs`).

#### Step 2: Run Backend Tests
```bash
pytest tests/
```

#### Step 3: Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
Frontend Dashboard will be live at `http://localhost:3000`.

---

### Option B: Docker Compose Execution

```bash
# Spin up PostgreSQL, ChromaDB, and FastAPI backend services
docker-compose up --build -d
```

---

## 🔌 API Endpoint Specifications & cURL Examples

### 1. Generate Problem & Run Differential Verification
```bash
curl -X POST "http://localhost:8080/api/problems/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Dynamic Programming",
    "difficulty": "Medium",
    "target_complexity": "O(N log N)",
    "educational_objective": "Prefix XOR frequency hash map pattern"
  }'
```

### 2. Generate & Rank Testcases for Existing Problem
```bash
curl -X POST "http://localhost:8080/api/testcases/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "statement_or_url": "Given an array of N integers, find maximum subarray sum.",
    "num_cases": 15,
    "include_adversarial": true
  }'
```

### 3. Switch Local Model Provider at Runtime
```bash
curl -X POST "http://localhost:8080/api/models/switch" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_type": "openai_compatible",
    "model_name": "qwen2.5-coder",
    "api_base": "http://localhost:1234/v1"
  }'
```

### 4. Export LeetCode Zip Package
```bash
curl -X POST "http://localhost:8080/api/export/leetcode" \
  -H "Content-Type: application/json" \
  -d @./examples/example_problem.json \
  --output problem_package.zip
```

---

## 📊 Quality Gate Scoring System

Every generated problem package is scored out of **100 points**:

| Metric | Max Score | Description |
| :--- | :--- | :--- |
| **Originality** | 30 | Cosine similarity against local ChromaDB corpus ($< 0.35$ similarity earns 30 points). |
| **Clarity** | 20 | Unambiguous problem statement, clear input/output specs, and worked examples. |
| **Correctness** | 25 | 100% output match between brute-force ($O(N^2)$) and optimal ($O(N)$) Python code. |
| **Test Coverage** | 15 | High coverage across boundary cases, min/max limits, and adversarial inputs. |
| **Educational Value** | 10 | Comprehensive editorial with step-by-step walkthrough and common pitfalls. |

> **Export Constraint**: Packages scoring $< 85.0$ points are rejected by the export pipeline to ensure problem quality.
