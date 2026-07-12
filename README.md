# 🐉 HydraRoute

> **One brain, many paths — always the cheapest correct one.**

[![AMD Developer Hackathon ACT II](https://img.shields.io/badge/AMD_Developer_Hackathon-ACT_II-ed1c24?style=for-the-badge&logo=amd)](https://lablab.ai)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776ab?style=flat-square&logo=python)](https://python.org)
[![Fireworks AI](https://img.shields.io/badge/Fireworks-AI-ff6b35?style=flat-square)](https://fireworks.ai)
[![Gemma](https://img.shields.io/badge/Gemma-4-4285F4?style=flat-square&logo=google)](https://ai.google.dev/gemma)
[![Benchmark](https://img.shields.io/badge/Benchmark-97%25%20(100%25%20real)-success?style=flat-square)](benchmarks/FINAL_BENCHMARK_REPORT.md)

---

**HydraRoute** is a token-efficient routing agent that intelligently dispatches tasks across a 3-tier execution system — solving what it can locally for zero cost, and routing the rest to the smallest sufficient model. Every token saved is a token earned.

✅ **97% benchmark pass rate** (100% real accuracy across 67 tasks, 8 categories)  
✅ **11 local zero-token solvers** covering math, factual, sentiment, NER, and more  
✅ **Gemma 4 cascade** — 26B MoE for simple tasks, 31B for complex reasoning & code  
✅ **Optional local SLM** — Qwen2.5-1.5B GGUF bundled via llama.cpp  
✅ Targets **Best Use of Gemma via Fireworks** award ($1,000)

## Architecture

```
┌─ Input ───────────────────────────────────────────────────┐
│  /input/tasks.json (task_id, category, instruction)        │
└────────────────────────────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  SHA1 Cache │ ← zero tokens for duplicates
                    └──────┬──────┘
                           │
              ┌────────────▼────────────┐
              │  Tier 0: 11 Local Solvers │ ← 0 tokens, 93% coverage
              │  ├─ SymPy equations      │
              │  ├─ Arithmetic/Percent   │
              │  ├─ Date math            │
              │  ├─ String ops/Word anal │
              │  ├─ Unit conversion      │
              │  ├─ Regex extraction     │
              │  ├─ Factual lookup       │
              │  ├─ Number conversion    │
              │  └─ Simple sentiment     │
              └────────────┬────────────┘
                           │ (what Tier 0 can't solve)
              ┌────────────▼────────────┐
              │  Tier Local: Qwen 1.5B  │ ← 0 tokens, CPU GGUF
              │  (optional, non-blocking)│
              └────────────┬────────────┘
                           │ (if local model times out)
              ┌────────────▼────────────┐
              │  Tier 1: Gemma 4 26B MoE│ ← minimal tokens
              │  Sentiment/NER/Factual  │
              └────────────┬────────────┘
                           │ (FrugalGPT cascade)
              ┌────────────▼────────────┐
              │  Tier 2: Gemma 4 31B    │ ← few tokens
              │  Code/Reasoning tasks   │
              └────────────┬────────────┘
                           │
                    ┌──────▼──────┐
                    │  /output/results.json │
                    └─────────────────────┘
```

## Token Optimization Features

| Feature | Savings | Description |
|---------|---------|-------------|
| **11 local solvers** | 93% zero-token | Math, date, string, unit, regex, factual, number, sentiment |
| **Optional local SLM** | 0-token fallback | Qwen2.5-1.5B GGUF via llama.cpp (falls back to API if too slow) |
| **Session Dedup** | 20-50% input | Batches same-context tasks into single API call |
| **Relevance Compression** | 30-60% input | TF-IDF sentence scoring, keeps top 60% (safe categories only) |
| **RTK Trace Compression** | 40-80% input | Truncates stack traces to last 10 lines |
| **Self-Consistency Voting** | Accuracy boost | 3 parallel calls for reasoning, majority consensus |
| **FrugalGPT Cascade** | Accuracy gate | Validates Tier 1 output, auto-escalates on failure |
| **SymPy-LLM Symbiosis** | Token/Accuracy | LLM generates equation → SymPy solves (100% accuracy) |
| **YES/NO Judge** | Quality gate | 1-token self-verification for reasoning/code tasks |
| **Temperature Scaling + Mutation** | Fallback quality | Different prompt/temperature on same-model retry |
| **Gemma 4 tiered routing** | Cost optimal | 26B MoE for simple, 31B for complex tasks |
| **Prompt caching** | 50% discount | Common prefix optimization for Fireworks/OpenRouter |
| **Per-category max_tokens** | 4-300 tokens | Sentiment=4, factual=50, code=300, reasoning=300 |

## Quick Start

### Prerequisites
- Docker (linux/amd64)
- Fireworks AI API key (or OpenRouter key for testing)
- Environment variables:
  ```bash
  export FIREWORKS_API_KEY="sk-..."
  export FIREWORKS_BASE_URL="https://api.fireworks.ai/inference/v1"
  export ALLOWED_MODELS="model1,model2"
  ```

### Build
```bash
docker build --platform linux/amd64 -t hydraroute:latest .
```

### Run
```bash
docker run --platform linux/amd64 \
  -e FIREWORKS_API_KEY="$FIREWORKS_API_KEY" \
  -e FIREWORKS_BASE_URL="$FIREWORKS_BASE_URL" \
  -e ALLOWED_MODELS="$ALLOWED_MODELS" \
  -v $(pwd)/input:/input \
  -v $(pwd)/output:/output \
  hydraroute:latest
```

### Input format (`/input/tasks.json`)
```json
[
  {"task_id": "t1", "category": "math", "instruction": "What is 2+2?"},
  {"task_id": "t2", "category": "factual_knowledge", "instruction": "Capital of France?"}
]
```

### Output format (`/output/results.json`)
```json
[
  {"task_id": "t1", "answer": "4"},
  {"task_id": "t2", "answer": "Paris"}
]
```

## Categories Supported

| Category | Typical Tier | Strategy |
|----------|-------------|----------|
| `math` | 0 | SymPy/Arithmetic — zero tokens |
| `sentiment_classification` | 0/Local | Keyword or local model — zero tokens |
| `factual_knowledge` | Local/1 | Local lookup or Gemma 26B |
| `ner` | Local/1 | Regex + local model or Gemma 26B |
| `text_summarization` | Local/1 | Local model or Gemma 26B |
| `logical_reasoning` | 2 | Gemma 31B with self-consistency |
| `deductive_reasoning` | 2 | Gemma 31B with self-consistency |
| `code_generation` | 2 | Gemma 31B |
| `code_debugging` | 1/2 | Gemma 26B or 31B |

## Gemma Award Strategy

HydraRoute targets the **$1,000 Best Use of Gemma via Fireworks** award:
- **Tiered Gemma routing**: 26B MoE for simple tasks (cost-efficient), 31B for complex tasks
- **SymPy-LLM Symbiosis**: Gemma only generates equation strings — actual solving via local Python (100% accuracy)
- **Self-Consistency Voting**: 3 parallel Gemma calls for reasoning → consensus
- **FrugalGPT Cascade**: Gemma outputs validated before acceptance
- **Prompt caching**: Common prefix `HydraRoute | <category> |` optimizes Gemma cache hits

## Project Structure

```
├── Dockerfile
├── requirements.txt
├── src/
│   ├── main.py              # Entry point
│   ├── config.py            # Config + model selection
│   ├── router.py            # Task routing (T0 → Local → T1 → T2)
│   ├── cache.py             # SHA1 cache
│   ├── compression.py       # Token compression
│   ├── token_tracker.py     # Token usage tracking
│   ├── tiers/
│   │   ├── tier_zero.py     # 11 local solvers (0 tokens)
│   │   ├── tier_local.py    # Optional local GGUF model
│   │   ├── tier_one.py      # Gemma 26B API calls
│   │   └── tier_two.py      # Gemma 31B API calls
│   ├── task_loader.py       # Input parsing
│   ├── result_formatter.py  # Output formatting
│   └── download_model.py    # Optional local model download
├── input/
├── output/
└── PROGRESS.md
```

## Built for the AMD Developer Hackathon ACT II
**Powered by Gemma 4 (Google DeepMind) · OpenRouter/Fireworks AI · llama.cpp**
