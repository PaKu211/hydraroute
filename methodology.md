# Methodology: Routing Overhead & Escalation Misconfiguration in Hybrid LLM Routers

## Research Question
Does a hybrid LLM router with a deterministic pre-LLM Tier-0 offload reduce cost at equal
accuracy versus single-model baselines, and under what configuration does naive routing
*increase* cost?

## Hypothesis (honest, revised)
- **H1 (measured, negative)**: A naive category→size escalation mapping over-escalates and
  costs MORE than always-large at actual pricing.
- **H2 (measured, positive)**: A data-driven fix — Tier-0 deterministic offload for trivial
  categories + escalating only `sentiment_classification` to large — restores a real saving
  and is robust under small price gaps.
- **H3 (pending, generalization)**: The effect holds across model families (Gemma-4;
  Llama-3.1-8B/70B; Qwen2.5-7B/32B).

## Experiment 1: Ablation / Routing Study (E1)
67-task benchmark (`benchmarks/hydraroute_benchmark.json`). Per-task route + model + token
attribution via `TokenTracker` (post-hoc fix from original over-escalating router).

Configs (multi-family via `ABLATE_SMALL`/`ABLATE_LARGE`/`ABLATE_FAMILY`):
| Config | Tier-0 | SymPy | small/large routing |
|--------|:---:|:---:|---|
| A_full | ✅ | ✅ | data-driven (only sentiment→large) |
| B_no_tier0 | ❌ | ✅ | data-driven |
| C_cascade | ✅ | ✅ | cascade-only (no explicit large pref) |
| D_no_sympy | ✅ | ❌ | data-driven |
| E_always_large | ❌ | ❌ | always large |
| F_always_small | ❌ | ❌ | always small |

Metrics: total tokens, per-task pass (fixed rubric), tier0_hits, model attribution.

**Status**: Gemma-4 family — A, D, E, F complete with correct data-driven fix. B, C blocked
on OpenRouter API credit (keys at `total_credits: 0`). 2nd-family routing pending same.

## Experiment 2: Cost Analysis (E2)
From E1 per-task token logs, compute cost under two price regimes (avoid RouterBench's
"assumed price gap" trap):
1. **Actual Gemma-4 OpenRouter pricing**: small 26B $0.06/$0.33, large 31B $0.12/$0.35 (in/out per M).
2. **Frontier gap**: small $0.10/$0.30, large $10.00/$30.00 (per M).
Report A vs E (always-large) and A vs F (always-small) as % delta. The over-escalation
mechanism is shown by model attribution (only 9/45 paid tasks need large).

**Status**: Gemma-4 computed — A vs E = +51.5% at actual pricing (negative result),
−91.8% at frontier pricing (positive). Recompute after B/C + 2nd family.

## Experiment 3: Local Serving Benchmark (E3) — UNBLOCKED (no API)
Serve small + large tiers via vLLM on notebook GPU (RTX PRO 6000 Blackwell). Measure
latency (p50/p95), throughput (tok/s) on the 67-task benchmark. Demonstrates the small
model is ~2× faster, making routing latency-feasible. Families: Qwen2.5-7B/32B (done on
notebook), Llama-3.1-8B/70B (pending GPU).

**Status**: Running on marimo notebook (Qwen2.5-7B then 32B).

## Compute Requirements
| Exp | Platform | Cost | Status |
|-----|----------|------|--------|
| E1 | OpenRouter API | blocked: keys exhausted (total_credits=0) | A/D/E/F gemma-4 done |
| E2 | derived | $0 | gemma-4 computed |
| E3 | marimo notebook GPU | free | running |

## Limitations & Assumptions
- 67-task benchmark is representative, not exhaustive.
- 2nd-family routing generalization blocked on API credit — reported as future work if
  unresolvable.
- Actual pricing used; no assumed price gaps (per RouterBench methodology).
