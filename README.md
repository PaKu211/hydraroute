# 🐉 HydraRoute

> **One brain, many paths — always the cheapest correct one.**

[![AMD Developer Hackathon ACT II](https://img.shields.io/badge/AMD_Developer_Hackathon-ACT_II-ed1c24?style=for-the-badge&logo=amd)](https://lablab.ai)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776ab?style=flat-square&logo=python)](https://python.org)
[![Fireworks AI](https://img.shields.io/badge/Fireworks-AI-ff6b35?style=flat-square)](https://fireworks.ai)

---

**HydraRoute** is a token-efficient routing agent that intelligently dispatches tasks across a 3-tier execution system — solving what it can locally for zero cost, and routing the rest to the smallest sufficient model. Every token saved is a token earned.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      HydraRoute Agent                       │
│                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────────┐  │
│  │ Classifier│───▶│   Router     │───▶│   Executor        │  │
│  │ (Regex +  │    │ (Tier 0/1/2) │    │                   │  │
│  │  Heuristic│    │              │    │  Tier 0: Local    │  │
│  │  Rules)   │    │              │    │  ├─ Python eval   │  │
│  └──────────┘    └──────────────┘    │  ├─ SymPy solver  │  │
│                                      │  └─ Regex/Rules   │  │
│       ┌─────────────────────────┐    │                   │  │
│       │    tasks.json (/input)  │    │  Tier 1: Small LLM│  │
│       │    ───────────────────  │    │  └─ Simple tasks  │  │
│       │    Read tasks on boot   │    │                   │  │
│       └─────────────────────────┘    │  Tier 2: Large LLM│  │
│                                      │  └─ Complex tasks │  │
│       ┌─────────────────────────┐    └───────────────────┘  │
│       │  results.json (/output) │                           │
│       │  ───────────────────────│                           │
│       │  Write results on exit  │                           │
│       └─────────────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
                          │
                    Fireworks AI API
                   (OpenAI-compatible)
```

## How It Works

### 3-Tier Execution System

| Tier | Engine | Cost | Used For |
|------|--------|------|----------|
| **Tier 0** | Local Python (eval, sympy, regex) | **$0.00** | Math equations, simple factual lookups, pattern matching |
| **Tier 1** | Smallest available LLM | **$** | Sentiment classification, NER, simple Q&A |
| **Tier 2** | Largest available LLM | **$$** | Code generation, debugging, summarization, complex reasoning |

### Task Categories

| Category | Typical Tier | Strategy |
|----------|-------------|----------|
| `factual_knowledge` | 0 → 1 | Regex lookup first, fall back to small model |
| `math` | 0 | Python eval / SymPy — zero API calls |
| `sentiment_classification` | 1 | Small model, tight max_tokens |
| `text_summarization` | 2 | Large model for quality, capped output |
| `ner` | 1 | Small model with structured prompt |
| `code_debugging` | 2 | Large model for reasoning |
| `logical_reasoning` | 1 → 2 | Simple syllogisms local, complex to large model |
| `code_generation` | 2 | Large model for correctness |

## Token Optimization Strategies

1. **Zero-cost local execution** — Math and pattern-matching tasks never touch the API
2. **Model-right-sizing** — Each task routes to the smallest model that can handle it
3. **System prompt compression** — All system prompts kept under 50 tokens
4. **Strict max_tokens budgets** — Per-category output caps prevent token waste
5. **No unnecessary context** — Prompts are surgical, no padding or preamble
6. **Fail-fast with fallbacks** — If Tier 0 fails, escalate to Tier 1/2 without retries

## Quick Start

### Prerequisites

- Docker (with `linux/amd64` support)
- Fireworks AI API key
- Environment variables set:
  ```bash
  export FIREWORKS_API_KEY="your-api-key"
  export FIREWORKS_BASE_URL="https://api.fireworks.ai/inference/v1"
  export ALLOWED_MODELS="accounts/fireworks/models/llama-v3p1-8b-instruct,accounts/fireworks/models/llama-v3p1-70b-instruct"
  ```

### Build

```bash
./scripts/build.sh
# or manually:
docker build --platform linux/amd64 -t hydraroute:latest .
```

### Run

```bash
./scripts/run.sh
# or manually:
docker run --platform linux/amd64 \
  -e FIREWORKS_API_KEY="$FIREWORKS_API_KEY" \
  -e FIREWORKS_BASE_URL="$FIREWORKS_BASE_URL" \
  -e ALLOWED_MODELS="$ALLOWED_MODELS" \
  -v $(pwd)/input:/input \
  -v $(pwd)/output:/output \
  hydraroute:latest
```

### Local Development

```bash
# Using docker-compose
docker compose up --build

# Or run directly with Python
pip install -r requirements.txt
python -m src.main
```

### Output

Results are written to `./output/results.json`:

```json
[
  {
    "task_id": "task_001",
    "response": "Paris",
    "model_used": "local",
    "tokens_used": 0,
    "tier": 0
  }
]
```

## Project Structure

```
hackathon-lablab/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py          # Entry point — read tasks, route, write results
│   ├── classifier.py    # Task category detection & tier assignment
│   ├── router.py        # Routes tasks to appropriate executor
│   ├── executors/
│   │   ├── local.py     # Tier 0 — eval, sympy, regex
│   │   ├── llm.py       # Tier 1 & 2 — Fireworks AI API calls
│   └── config.py        # Model config, token budgets, env vars
├── input/
│   └── tasks.json       # Input tasks (mounted at /input)
├── output/               # Output results (mounted at /output)
├── scripts/
│   ├── build.sh
│   └── run.sh
└── research/             # Research notes & experiments
```

## Team

> 🏗️ *Team info placeholder — update before submission*

| Role | Name |
|------|------|
| Lead Developer | TBD |
| Architecture | TBD |

---

<p align="center">
  Built for the <strong>AMD Developer Hackathon ACT II</strong> on <a href="https://lablab.ai">lablab.ai</a><br/>
  Powered by <strong>Fireworks AI</strong> · Running on <strong>AMD Instinct™</strong>
</p>
