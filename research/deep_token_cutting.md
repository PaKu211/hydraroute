# Deep Research — Facet 1: Token-Cutting & Pre-LLM Solvers

## Summary
A large body of work compresses or prunes LLM prompts/tokens to cut cost: LLMLingua
1/2 (text compression via a small LM), Selective Context (information-entropy pruning),
LongLLMLingua (long-context prompt compression, ~20× token cut, ~4× speedup), Scissorhands
(attention-based KV cache eviction). Speculative decoding (Leviathan et al. 2023; Chen
et al. 2023) and its "Medusa"/"EAGLE" successors cut *decoding* latency, not input tokens.
CascadeBERT and HybridLLM route across *model sizes*, not free deterministic tiers.

## Key Findings
- **LLMLingua / LLMLingua-2** (Jiang et al. 2023a, 2023b): prompt compression via a
  small task-agnostic LM; 10–20× compression with small quality loss.
- **Selective Context** (Li 2023): drop low-information context by self-information.
- **LongLLMLingua** (Jiang et al. 2023c): long-doc compression, recovers or beats
  uncompressed accuracy at ~20× fewer tokens.
- **Scissorhands** (Liu et al. 2023): KV-cache eviction, "attention sinks."
- **FrugalGPT** (Chen et al. 2023): cascades + prompt caching + LLM selection; reports
  98% of GPT-4 quality at 98% cost cut — but via *prompt caching*, not free solvers.
- **HybridLLM** (Ding et al. 2024): routes each token between a cheap and an expensive
  model.

## Identified Gap (OUR NOVELTY)
**No prior work uses deterministic, free, pre-LLM solvers (regex / lookup / arithmetic
evaluation) as Tier-0 offload.** The literature cuts *tokens* or *chooses a cheaper LLM*,
but never *skips the LLM entirely* for trivially-solvable categories. This is the gap
HydraRoute fills: Tier-0 deterministically resolves sentiment/factual/arithmetic classes
at zero token cost, something token-compression and model-cascade methods do not address.

## References (verified)
- Jiang et al. 2023a. "LLMLingua: Compressing Prompts for Accelerated Inference of LLMs."
  arXiv:2310.05736.
- Jiang et al. 2023b. "LLMLingua-2: Data Distillation for Efficient Prompt Compression."
  arXiv:2403.12968.
- Jiang et al. 2023c. "LongLLMLingua: Accelerating and Enhancing LLMs in Long Context
  Scenarios via Prompt Compression." arXiv:2310.06839.
- Li. 2023. "Selective Context: Compressing Context for LLM Inference." arXiv:2304.12102.
- Liu et al. 2023. "Scissorhands: Exploiting the Persistence of Important Tokens for
  Long-Context LLM Inference." arXiv:2305.17118.
- Chen et al. 2023. "FrugalGPT: How to Use Large Language Models While Reducing Cost and
  Improving Performance." arXiv:2305.05176.
- Ding et al. 2024. "Hybrid LLM: Cost-Efficient and Quality-Aware Query Routing." ICLR 2024.
  arXiv:2404.14618.
- Leviathan et al. 2023. "Fast Inference from Transformers via Speculative Decoding."
  arXiv:2211.17192.
