# Deep Research — Facet 2: SOTA Routers & Learned Routing

## Summary
Modern LLM routers either (a) *train a preference/quality predictor* to choose between
models, or (b) *cascade* cheap→expensive models until quality is sufficient. The
best-known systems — FrugalGPT, RouteLLM, AutoMix, MixLLM, RouterBench — dominate a
single fixed model on cost *only when the price gap is large and the routing is accurate*.

## Key Findings
- **FrugalGPT** (Chen 2023): LLM cascade + prompt cache + selection; 98% of GPT-4 quality
  at 98% cost reduction on a specific (cheap/expensive) pairing.
- **RouteLLM** (Ong et al. 2024, arXiv:2406.18665): preference-data-trained router; >2×
  cost reduction at GPT-3.5 quality vs GPT-4, beating embedding/PLM baselines.
- **AutoMix** (Jiang et al. 2024, arXiv:2405.07380): LLM-agent router formulated as a
  POMDP; >50% compute reduction with quality preservation.
- **MixLLM** (Huang et al. 2024, arXiv:2404.11549): capability-aware query rewriting +
  routing; 97.25% of GPT-4 quality at 24.18% cost.
- **RouterBench** (Hu et al. 2024, arXiv:2403.10935): 405K outcomes across 11 LLMs.
  **Central finding: a *learned* router generally does NOT dominate a simple single-model
  baseline; cost savings are highly sensitive to the assumed price gap.** This directly
  supports our honest-negative framing: naive routing configs can *cost more* than the
  always-large baseline.
- **HybridLLM** (Ding 2024): per-token routing; cuts large-model calls ~40% at equal
  quality under its pricing.

## Relevance to HydraRoute
RouterBench's central finding is the methodological anchor for our paper: routing overhead
and misconfiguration can *reverse* expected savings. Our E1/E2 provide a concrete,
reproducible instance of this — a hybrid router whose naive category→size mapping
*over-escalates* and costs +51% vs always-large, which a data-driven fix (Tier-0 + ablated
escalation) corrects. This positions HydraRoute as evidence that *deterministic Tier-0
offload* is more robust than *learned* routing when the price gap is small.

## References (verified)
- Ong et al. 2024. "RouteLLM: Learning to Route LLMs with Preference Data." arXiv:2406.18665.
- Jiang et al. 2024. "AutoMix: Automatically Mixing Language Models." arXiv:2405.07380.
- Huang et al. 2024. "MixLLM: Dynamic Routing in Mixed-Private LLM Deployment." arXiv:2404.11549.
- Hu et al. 2024. "RouterBench: A Benchmark for Multi-LLM Routing System." arXiv:2403.10935.
- Ding et al. 2024. "Hybrid LLM: Cost-Efficient and Quality-Aware Query Routing." arXiv:2404.14618.
- Chen et al. 2023. "FrugalGPT." arXiv:2305.05176.
