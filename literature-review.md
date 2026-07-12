# Literature Review: Hybrid Token-Efficient Routing Agents

## Summary

This review synthesizes findings across four facets: (1) academic papers on LLM routing cascades and token efficiency, (2) competing submissions from the AMD Developer Hackathon ACT II Track 1, (3) open-source GitHub repositories for LLM routing and prompt compression, and (4) advanced Fireworks AI API capabilities. The literature and competitive landscape reveal that winning routing agents share three core strategies: zero-token deterministic pre-processing for math/pattern tasks, a learned or heuristic small-to-large model cascade with validation gating, and aggressive token budget control via per-category `max_tokens`, stop sequences, and reasoning suppression. The strongest verified competitor (SebAustin) achieves 99.5% accuracy with 32.5% zero-token tasks and ~47-51% token reduction using a single-escalation cascade with format-based confidence gating. Another strong competitor (realjunjiejj) uses a local 1.5B Qwen model via llama.cpp to handle constrained tasks with zero Fireworks token cost. FrugalGPT (Chen et al., 2023) provides the theoretical foundation with 98% cost reduction vs. GPT-4 via learned cascades. RouteLLM (Ong et al., 2024) extends this with preference-trained routers achieving 2x cost reduction. Key gaps include limited published work on "smoke testing" (small-model-first validation before routing) and the absence of prompt caching exploitation in most hackathon submissions.

## Key Findings by Facet

### Facet 1: Academic Papers on LLM Routing and Token Efficiency

- **FrugalGPT** (Chen, Zaharia, Zou, 2023) — arXiv:2305.05176. Foundational paper establishing the LLM cascade framework. Proposes three strategies: prompt adaptation, LLM approximation, and LLM cascade. Demonstrates matching GPT-4 performance with up to **98% cost reduction**, or improving GPT-4 accuracy by 4% at the same cost. Core insight: different queries should use different models; a learned cascade selector can optimize the cost-quality Pareto frontier. The paper's cascade architecture (small model → medium model → large model with gating) directly inspired the hydraroute tier system.

- **RouteLLM** (Ong et al., 2024) — arXiv:2406.18665. Extends FrugalGPT with routers trained on human preference data using BERT, matrix factorization, and causal LLM routers. Achieves **2x cost reduction** without quality loss on Chatbot Arena benchmarks. Key contribution: routers transfer across model pairs at test time without retraining. The open-source framework (lm-sys/RouteLLM, ★5,200) is a drop-in OpenAI client replacement via LiteLLM — directly applicable to our Fireworks AI integration.

- **Mixture-of-Agents (MoA)** (Wang et al., 2024) — arXiv:2406.04692. Proposes layered architecture where each layer comprises multiple LLM agents; each agent consumes outputs from the previous layer as auxiliary context. Achieves state-of-the-art on AlpacaEval 2.0 (65.1% vs GPT-4 Omni's 57.5%). While MoA is designed for quality rather than token efficiency, its layered aggregation concept inspired our cascade validation gating.

- **LLMLingua** (Jiang et al., 2023) — arXiv:2310.05736, EMNLP 2023. Coarse-to-fine prompt compression achieving **up to 20x compression** with minimal performance loss. Uses budget controller for semantic integrity, token-level iterative compression, and instruction tuning for distribution alignment. GitHub: microsoft/LLMLingua (★6,426). Our heuristic cleaner draws inspiration from this but avoids the dependency overhead.

- **Speculative Decoding** (Leviathan et al., 2022; Chen et al., 2023) — draft-then-verify parallelism achieving 2-3x latency reduction. Not directly applicable to our batch JSON task format but informs our thinking about efficient token usage.

- **SplitLLM** — Explainable hybrid routing + multi-stage reasoning. No verified paper found; appears to be a hackathon concept name.

### Facet 2: Winning Hackathon Write-ups & Competitor Analysis

**SebAustin/amd-routing-agent** (verified GitHub, strongest competitor):
- 99.5% accuracy on 200-task evalset, 32.5% tasks at zero tokens (Tier 0: arithmetic, date math, string ops, unit conversion, regex)
- **47-51% token reduction** vs naive strongest-model baseline
- Total cost: **$0.003636** for 200 tasks (price-weighted)
- Only 17,157 total tokens (12,110 prompt / 5,047 completion)
- Wall time: 23.2s with 8-way concurrency
- Route distribution: 65 tier0, 76 tier1 gpt-oss-20b, 48 tier1 gpt-oss-120b, 10 tier1 deepseek-v4-flash, 1 tier2 deepseek-v4-pro
- Architecture: deterministic solvers → cheapest adequate model → single escalation to strongest model
- ConfidenceGate: primary = output-format validation + Tier-0 cross-check; secondary = answer-token logprobs (unwired)
- Reasoning suppression per model profile (registry-driven)
- Gemma-aware routing preference (tiebreak)
- **Key innovation**: Single-escalation policy (max 2 model calls per task, never loops), no self-verification LLM calls

**realjunjiejj/fireworks-router-agent** (verified GitHub, second strongest):
- Local Qwen2.5 1.5B GGUF Q4_K_M via llama.cpp (~1.12 GB, fits 4 GB limit)
- Pre-assigns hardness score 1-5 locally (0 tokens) before any API call
- 8 tasks: 3 zero-token routes, 5 Fireworks calls, **1,048 total tokens** (666 input / 382 output)
- Category-aware model preferences: GPT-OSS 120B for factual/NER/debugging/code, MiniMax M3 for math/logic
- Graceful fallback: if local model fails to start, disable and continue
- **Key innovation**: Local llama.cpp model for constrained summaries (verifiable word count, etc.)

**mauriciorojassan** (verified lablab submission):
- PACT protocol: ~40 bytes per routing signal vs ~200+ for conventional approaches
- Multi-tier cascade with quality gating

**HarshitBilagi** (verified lablab submission):
- Local NPU inference with Phi-3.5-mini INT4 on Intel AI Boost NPU
- Demonstrates hardware-specific optimization for token-free inference

**Common winning patterns across all competitors**:
1. Tier 0 deterministic solvers for math/patterns — universal, non-negotiable
2. Local model inference for constrained tasks (llama.cpp, ONNX, NPU)
3. Per-category model selection, never one-size-fits-all
4. Validation gating before escalation (format check, cross-check, length)
5. Reasoning suppression for non-reasoning models (saves 100-2000 tokens/call)
6. Single-escalation policy — max 2 model calls per task, never loop

### Facet 3: Open-Source GitHub Repositories

- **RouteLLM** — lm-sys/RouteLLM ★5,200. Drop-in OpenAI client replacement. Routers: MF, BERT, sw_ranking, causal_llm. Supports any OpenAI-compatible endpoint including Fireworks.

- **LLMLingua** — microsoft/LLMLingua ★6,426. Prompt compression up to 20x. Pure Python — works as pre-processor before any API call. Low dependency overhead.

- **opensquilla** — opensquilla/opensquilla ★5,773. Token-efficient AI agent framework. Apache-2.0. Supports OpenAI-compatible APIs.

- **NVIDIA Model Optimizer** — NVIDIA/Model-Optimizer ★3,206. Speculative decoding, quantization, pruning. NVIDIA-specific but techniques are architecture-independent.

- **browserwing** — ★1,350. Token-efficient browser automation. Uses JSON config — compatible pattern for our Docker-based submission.

- **SpecForge** — sgl-project/SpecForge ★985. Train/deploy speculative decoding for SGLang. Demonstrates feasibility of speculative techniques in production.

- **pi-mcp-adapter** — ★982. Token-efficient MCP adapter pattern.

- **clawcodex** — ★792. Claude Code rebuild claiming 200x cost saving. CLI-based, reads/writes files — similar contract to our JSON adapter.

### Facet 4: Fireworks AI Advanced Capabilities

- **Prompt Caching**: Enabled by default for all chat completion calls. Provides **50% discount** on cached input tokens. Cached segments span from the first token of the message list to the first newline after the last `user` message. Session affinity via `user` parameter or `prompt_cache_key`. `prompt_cache_isolation_key` for tenant isolation.

- **Structured Outputs**: Two modes — `json_object` (constrained to valid JSON) and `json_schema` (adheres to provided JSON Schema 2020-12 schema). Schema mode supports `anyOf`/`allOf`/`$ref`/recursive schemas. Grammar mode enables BNF grammar constraints. **Use `json_schema` for task answer formatting to guarantee parseable outputs.**

- **Batch API**: 50% off serverless pricing. JSONL format, max 1GB. Good for offline eval but not for real-time judging.

- **Rate Limits**: Global ceiling ~21.6M TPM prompt / 5.4M uncached / 216k generated. Adaptive — 429 requires exponential backoff. Priority tier reduces 503 load-shed events.

- **Router Service**: Traffic splitting by replica count. Used for A/B testing, traffic migration, zero-downtime swaps. Not directly useful for per-request routing.

- **Key Parameters for Token Efficiency**:
  - `temperature`: 0.0 for deterministic structured outputs, 0.3 for creative
  - `max_tokens`: **per-category caps** (4 for sentiment, 500 for code)
  - `stop`: Use `\n` stop sequence for single-line answers
  - `reasoning_effort`: Set `"none"` or `"low"` for non-reasoning tasks
  - `thinking`: Disable for models that support it (saves reasoning tokens)
  - `perf_metrics_in_response`: Track latency per call
  - `safe_tokenization`: Ensure output fits within configured limits
  - `frequency_penalty`/`presence_penalty`: Minimize to avoid token waste

- **Available Models on AMD Hardware**:
  - Small: Llama 3.2 3B, Llama 3.1 8B, Mistral 7B, DeepSeek V4 Flash (~20B)
  - Large: DeepSeek V4 Pro, DeepSeek V3 (671B MoE), Llama 3.3 70B, Qwen 3 235B-A22B
  - GPT-OSS-20B: Lowest price at $0.07/$0.30 per 1M tokens

## Identified Gaps & Opportunities

1. **Prompt caching is largely unexploited in hackathon submissions**. No competitor's README mentions Fireworks' built-in 50% prompt caching discount. Our tiered system prompts with common prefixes could maximize cache hits.

2. **No competitor uses learned routers** — all use heuristic/rule-based routing. RouteLLM-style learned routers are a potential differentiator but require preference data. For the hackathon timescale, rule-based routing with tuned thresholds dominates.

3. **Local model inference is under-explored in our current architecture**. Competitors demonstrate local models (Qwen 1.5B, Phi-3.5-mini) for constrained tasks. Adding a lightweight local model would reduce Fireworks token spend for sentiment, NER, and constrained summarization.

4. **"Smoke testing" / tiny-model validation is not formally studied** in academic literature. The closest is Tiny QA Benchmark++ for lightweight LLM quality assurance (Koc, 2025). Our FrugalGPT-style validation cascade has no direct academic counterpart but is empirically validated by hackathon winners.

5. **Maximum token efficiency ceiling**: The theoretical minimum is Tier 0 for all tasks + perfect caching + zero reasoning tokens. The practical best is ~52-55% zero-token tasks (extending Tier 0 coverage) + local model for constrained tasks + 4-token sentiment outputs.

## Complete References

```
@article{chen2023frugalgpt,
  title={FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance},
  author={Chen, Lingjiao and Zaharia, Matei and Zou, James},
  journal={arXiv preprint arXiv:2305.05176},
  year={2023}
}

@article{ong2024routellm,
  title={RouteLLM: Learning to Route LLMs with Preference Data},
  author={Ong, Isaac and Almahairi, Amjad and Wu, Vincent and Chiang, Wei-Lin and Wu, Tianhao and Gonzalez, Joseph E and Kadous, M Waleed and Stoica, Ion},
  journal={arXiv preprint arXiv:2406.18665},
  year={2024}
}

@article{wang2024mixture,
  title={Mixture-of-Agents Enhances Large Language Model Capabilities},
  author={Wang, Junlin and Wang, Jue and Athiwaratkun, Ben and Zhang, Ce and Zou, James},
  journal={arXiv preprint arXiv:2406.04692},
  year={2024}
}

@article{jiang2023llmlingua,
  title={LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models},
  author={Jiang, Huiqiang and Wu, Qianhui and Lin, Chin-Yew and Yang, Yuqing and Qiu, Lili},
  journal={arXiv preprint arXiv:2310.05736},
  year={2023}
}

@article{leviathan2022speculative,
  title={Fast Inference from Transformers via Speculative Decoding},
  author={Leviathan, Yaniv and Kalman, Matan and Matias, Yossi},
  journal={arXiv preprint arXiv:2211.17192},
  year={2022}
}

@article{chen2023speculative,
  title={Speculative Sampling},
  author={Chen, Charlie and Borgeaud, Sebastian and Irving, Geoffrey and Lespiau, Jean-Baptiste and Sifre, Laurent and Jumper, John},
  journal={arXiv preprint arXiv:2302.01318},
  year={2023}
}
```
