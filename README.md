# 🧠 Program-Aided Reasoning Agent
### A Local-First LLM Agent Powered by Ollama and Qwen

A program-aided reasoning system that combines local Large Language Models (LLMs), Python code generation, sandboxed execution, self-consistency, and deterministic answer validation to solve structured reasoning problems.

**No cloud inference. No external API dependency. No hard-coded answers. Just local reasoning and executable problem-solving.**

---

## ✨ Key Features

- **100% Local Inference** — Uses Ollama with a locally installed Qwen model.
- **Program-Aided Reasoning** — Converts natural-language problems into executable Python programs.
- **Self-Consistency** — Generates multiple candidate programs and compares their results.
- **Reasoning Fallback** — Uses a secondary reasoning path when program-based solving is unsuccessful.
- **Deterministic Validation** — Cleans and validates answers against the requested output format.
- **Persian & English Support** — Designed to process problems in both languages.
- **Execution Time Limits** — Applies time limits to generated program execution.
- **Reliable Output Contract** — Produces structured JSON output, including when an error occurs.

## 🏗️ Architecture

The agent follows a modular pipeline:

```text
                  ┌──────────────────────┐
                  │   Problem Input      │
                  │      input.json      │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │    Problem Solver   │
                  │  Local LLM / Ollama  │
                  └──────────┬───────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
        ┌─────────────────┐    ┌─────────────────┐
        │ Program         │    │ Reasoning       │
        │ Generation      │    │ Fallback        │
        └────────┬────────┘    └────────┬────────┘
                 │                      │
                 ▼                      │
        ┌─────────────────┐             │
        │ Sandbox         │             │
        │ Execution       │             │
        └────────┬────────┘             │
                 │                      │
                 ▼                      │
        ┌─────────────────┐             │
        │ Candidate       │             │
        │ Evaluation      │             │
        └────────┬────────┘             │
                 │                      │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │ Formatter &         │
                 │ Answer Validator    │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │     output.json     │
                 └──────────────────────┘
```

### Core Components

| Component | Responsibility |
|---|---|
| **LLM Interface** | Communicates with the local Ollama server. |
| **Programmer** | Generates Python code to solve the problem. |
| **Sandbox** | Executes generated code with execution restrictions and time limits. |
| **Self-Consistency** | Up to 3 program samples (different temperatures / encodings); two agreeing answers are accepted, otherwise majority vote. |
| **Hints** | Short, generic, keyword-selected guidance (truth/liar, ordering, scheduling, percentages, sets, grid, graph, digits, algebra). No known question or answer is stored. |
| **Reasoner** | Provides a fallback reasoning path when needed. |
| **Formatter** | Normalizes and validates the final answer. |
| **Main Interface** | Handles input/output JSON and execution flow. |

---

## ⚙️ Requirements

- Python 3.10+
- [Ollama](https://ollama.com/)
- Sufficient RAM / GPU memory for the selected model
- The configured local Qwen model

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/melikaVafaei/LLM_Agent_Assignment_1_4041284042.git
cd LLM_Agent_Assignment_1_4041284042
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install and start Ollama

Download Ollama from:

https://ollama.com/

Start the Ollama service, then pull the required model:

```bash
ollama pull qwen3.8:27b
```

> The agent is configured for the instructor's model, `qwen3.8:27b`. It never silently falls back to another model.

### 4. Run the agent

```bash
python main.py --input input.json --output output.json
```

---

## 📥 Input Format

The agent receives a JSON object containing a problem identifier and a natural-language problem description.

**Example — `input.json`**

```json
{
  "id": "problem_001",
  "problem": "A number multiplied by 7 and increased by 13 equals 97. Find the number."
}
```

## 📤 Output Format

The agent writes the result to the specified output file.

**Example — `output.json`**

```json
{
  "id": "problem_001",
  "answer": "12"
}
```

The `answer` field contains the final answer rather than an explanation or internal reasoning trace.

---

## 🧩 Problem-Solving Strategy

The system is designed for structured reasoning tasks that can benefit from computation.

Examples include:

| Problem Family | Typical Approach |
|---|---|
| Arithmetic & Algebra | Exact calculations and equation solving |
| Ordering Constraints | Permutation search and constraint checking |
| Logical Statements | Truth-assignment enumeration |
| Scheduling | Dependency analysis and critical-path reasoning |
| Set Theory | Inclusion-exclusion and counting |
| Percentage Problems | Sequential arithmetic and inverse calculations |
| Assignment Problems | Constraint satisfaction and backtracking |
| Truth-Teller / Liar Puzzles | Logical case enumeration |
| Shortest Path | Graph search and path evaluation |
| Digit Constraints | Exhaustive search over valid candidates |

The agent does not rely on a fixed list of known questions. It attempts to construct a computational solution from the problem description.

---

## 🔧 Configuration

The agent supports environment-based configuration.

| Variable | Description |
|---|---|
| `OLLAMA_MODEL` | Local Ollama model tag |
| `TIME_BUDGET` | Overall time budget per problem, in seconds |
| `MAX_CODE_SAMPLES` | Maximum number of generated program candidates |
| `MAX_LLM_CALLS` | Maximum allowed LLM calls |
| `CODE_THINK` | Thinking configuration for code generation |
| `COT_THINK` | Thinking configuration for the reasoning fallback |
| `OLLAMA_CONTEXT` | Context window (default 3072) |
| `REQUEST_TIMEOUT` | Per-request timeout in seconds |
| `AGENT_DEBUG` | Set to `1` to print generated programs to stderr |

Example:

```bash
export OLLAMA_MODEL="qwen3.8:27b"
export TIME_BUDGET=240
export MAX_CODE_SAMPLES=5
export MAX_LLM_CALLS=8
```

Configuration defaults and additional limits are defined in:

```text
source/agent/config.py
```

---

## 📁 Project Structure

```text
LLM_Agent_Assignment_1_4041284042/
│
├── main.py
├── requirements.txt
├── README.md
│
├── source/
│   ├── agent/
│   │   ├── config.py
│   │   ├── llm.py
│   │   ├── prompts.py
│   │   ├── solver.py
│   │   ├── sandbox.py
│   │   └── formatter.py
│   │
│   └── eval/
│       ├── run_eval.py
│       ├── gen.py / gen2.py   (problem generators with brute-force ground truth)
│       └── colab_eval.ipynb
│
```

**Module overview:**

- `main.py` — Command-line entry point and JSON interface.
- `config.py` — Model settings, execution budgets, and configurable limits.
- `llm.py` — Local Ollama communication.
- `prompts.py` — Instructions for program generation and reasoning.
- `solver.py` — Candidate generation, execution, and solution selection.
- `sandbox.py` — Restricted execution of generated Python code.
- `formatter.py` — Final answer extraction and format validation.
- `run_eval.py` — Evaluation entry point.

---

## 📊 Evaluation

The project includes an evaluation workflow for measuring performance across different reasoning problem families.

Run:

```bash
python source/eval/run_eval.py --per-family 10
python source/eval/run_eval.py --gen2 --per-family 4 --seed 5   # harder, structurally different problems
```

`gen2.py` marks problems with several valid answers as ambiguous; for those the literal `No unique solution` is accepted.

The evaluation workflow is intended to report:

- Overall accuracy
- Accuracy by problem family
- Persian vs. English performance
- Average execution time
- Average LLM calls

### Evaluation Principles

- Problems should be generated independently of the agent's solution logic.
- Ground-truth answers should be computed separately.
- Exact answer matching should be used when required by the evaluation protocol.
- Ambiguous questions should be identified rather than treated as having a unique answer.
- Performance should be measured across multiple problem instances, not only demonstration examples.

**Note:** Evaluation results depend on the selected model, hardware, prompts, execution limits, and test distribution. Actual accuracy should be reported from completed evaluation runs.

---

## 🔒 Local Execution & Safety

The LLM endpoint is restricted to the local Ollama service:

```text
http://localhost:11434
```

The system is designed to operate without cloud-based inference APIs or internet access during normal execution.

Generated Python programs are executed through a restricted subprocess environment with execution limits and code restrictions.

**Security note:** The execution restrictions are defense-in-depth measures, not a guarantee of complete isolation against malicious code. The sandbox should not be considered a hardened security boundary for untrusted workloads.

---

## 🎯 Design Goals

The project focuses on five main engineering goals:

1. **Generalization** — Solve unseen problems rather than memorize known answers.
2. **Computational Accuracy** — Use executable programs for problems that benefit from precise calculations.
3. **Efficiency** — Control model calls and execution time.
4. **Reliability** — Validate final answers and maintain a consistent JSON interface.
5. **Privacy** — Keep model inference and problem processing local.

---

## 🛠️ Troubleshooting

**Ollama connection refused**

Make sure the Ollama service is running:

```bash
ollama serve
```

**Model not found**

Check installed models:

```bash
ollama list
```

Pull the configured model if necessary:

```bash
ollama pull qwen3.8:27b
```

**Execution timeout**

Consider adjusting `TIME_BUDGET` or reviewing the generated program's search complexity.

**Invalid or empty answer**

Inspect the application logs and review the formatter and validation stages.

---

## 📌 Important Notes

- The project is designed for local execution using Ollama.
- The configured model must be available locally.
- The output format is intended to follow the instructor's JSON contract.
- Accuracy is not guaranteed for every unseen problem; it must be established through independent evaluation.
- The evaluation script and test results should be verified against the final submitted source code.

---

## 👨‍💻 Project Summary

**Program-Aided Reasoning Agent** explores a practical approach to improving LLM problem-solving by combining language understanding with executable computation.

Instead of relying exclusively on natural-language generation, the system attempts to translate reasoning tasks into Python programs, execute them, compare candidate results, and validate the final output.

**Local LLM + Program Synthesis + Execution + Validation = Program-Aided Reasoning.**