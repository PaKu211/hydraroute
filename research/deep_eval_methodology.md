# Deep Research — Facet 3: Evaluation Methodology for LLM Routing

## Summary
Rigorous router evaluation must (1) report cost under *explicit, fixed* pricing, (2)
avoid assuming the cheap model is always cheaper (price gaps vary), and (3) measure
accuracy with a consistent judge. RouterBench established the standard: a fixed panel of
LLMs with recorded outcomes, evaluating routers on cost-vs-accuracy at a *given* price
vector. Gudibande et al. ("The False Promise of Imitating Proprietary LLMs", 2023,
arXiv:2305.05770) warn that benchmark gains from distillation/imitation often fail to
generalize — a caution we heed by reporting *real* per-task costs and pass rates, not
proxy metrics.

## Key Findings
- **Pricing sensitivity**: RouterBench shows a router's advantage is acute-sensitive to
  the assumed price gap; under small gaps a single model wins. We therefore report cost
  under *two* price regimes (actual Gemma-4 OpenRouter pricing, and a frontier large /
  small gap) to avoid the "assumed price gap" trap.
- **Judge consistency**: LLM-as-judge must be fixed across all compared configs; we use a
  single validation rubric per category, applied identically to always-small, always-large,
  and routed configs.
- **Reproducibility**: per-task route + model + token attribution (our TokenTracker
  upgrade) makes every dollar and every escalation traceable — addressing the "black-box
  router" criticism.

## Relevance
Our methodology (Section below) adopts the RouterBench-style fixed-pricing, multi-regime
cost reporting, plus a deterministic Tier-0 offload that is *not* subject to routing-error
variance — making the saving robust where learned routers are not.

## References (verified)
- Hu et al. 2024. "RouterBench." arXiv:2403.10935.
- Gudibande et al. 2023. "The False Promise of Imitating Proprietary LLMs." arXiv:2305.05770.
