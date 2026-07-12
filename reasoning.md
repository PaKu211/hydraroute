# Research Deliberation: HydraRoute Competitive Positioning

## Knowledge Consolidation

The AMD Developer Hackathon ACT II Track 1 (Hybrid Token-Efficient Routing Agent) is a cost-optimization challenge with an accuracy gate. The evaluation is two-phase: (1) LLM-judge accuracy gate, then (2) ranking by total token consumption. Every competitor we analyzed converges on three non-negotiable strategies: Tier-0 deterministic solvers (0 tokens), per-category model selection, and validation-gated cascades. The strongest verified competitor (SebAustin) achieves 99.5% accuracy with 32.5% zero-token tasks and ~47-51% token reduction. Another strong competitor (realjunjiejj) uses a local 1.5B model via llama.cpp to handle constrained tasks at zero Fireworks token cost. Academic work confirms the theoretical foundation: FrugalGPT achieves 98% cost reduction via cascading, RouteLLM achieves 2x cost reduction via learned routing. Our current HydraRoute implementation (SymPy Tier 0, SHA1 cache, heuristic compression, FrugalGPT validation, category-specific max_tokens) is competitive but has clear gaps relative to top competitors.

## Knowledge Gaps & Contradictions

- **Gap 1**: No competitor uses Fireworks' built-in prompt caching (50% discount on cached input tokens). We're not exploiting it either.
- **Gap 2**: We have no local model inference for constrained tasks (sentiment, NER, simple summarization). competitors show 1.5B-3B local models can handle these at zero token cost.
- **Gap 3**: Our Tier-0 solvers only cover math (SymPy). Competitors extend Tier 0 to date math, string ops, unit conversion, and regex extraction — achieving 32.5% zero-token tasks.
- **Gap 4**: Our SHA1 cache is exact-match only. Semantic caching (SQLite + embeddings) could catch near-duplicates.
- **Contradiction**: Caveman-style prompt compression (aggressive removal) was found to strip logical constraints, but the winning SebAustin approach uses minimal prompts with task-type-specific templates. Our heuristic cleaner is safer but less aggressive.

## Candidate Hypotheses

### Hypothesis 1: Extend Tier-0 coverage + add local model = maximize zero-token tasks
- **Statement**: Expanding Tier-0 solvers to cover date math, string ops, unit conversion, regex, and simple classification (via a local 1.5B GGUF model) will push zero-token tasks from ~9% (1/11 sample tasks) to 30-50% of evaluation tasks.
- **Null hypothesis**: Most evaluation tasks require Fireworks API calls regardless of Tier-0/local coverage.
- **Required evidence**: Build extended solvers, test against the sample 11 tasks and any public evalsets.
- **Feasibility**: High — competitors prove this works. Local Qwen 2.5 1.5B GGUF is ~1.12 GB and fits within the 4 GB Docker limit.
- **Novelty**: Low (competitors already do this), but high impact — directly reduces token spend.
- **If confirmed**: Adds ~20-40% more zero-token tasks, directly improving ranking position.

### Hypothesis 2: Fireworks prompt caching exploitation yields 50% cost reduction on repeated prompts
- **Statement**: Structuring all system prompts with common prefixes will maximize Fireworks' built-in prompt cache hits, reducing effective input token cost by ~50% for cached segments.
- **Null hypothesis**: The evaluation tasks are sufficiently diverse that prompt caching provides negligible benefit.
- **Required evidence**: Measure cache hit rates with structured vs unstructured prompts.
- **Feasibility**: Very high — zero code change, just prompt restructuring. Fireworks caches from first token to last user message's first newline.
- **Novelty**: Medium — no competitor mentions exploiting this.
- **If confirmed**: Free 50% reduction on input tokens for any cached prefix, a pure competitive edge.

### Hypothesis 3: Single-escalation policy beats multi-cascade for accuracy + token efficiency
- **Statement**: A single escalation (Tier 1 → Tier 2, max 2 API calls total) with format-based confidence gating delivers higher accuracy and lower tokens than multi-cascade approaches with LLM self-verification.
- **Null hypothesis**: Multi-cascade (3+ tiers) or self-verification loops improve accuracy enough to justify the token cost.
- **Required evidence**: Compare our current FrugalGPT cascade (T1 → validate → T2) against 3-tier alternatives.
- **Feasibility**: Already implemented. Competitors confirm: SebAustin uses exactly this pattern (single escalation, no verification loops).
- **Novelty**: Low (competitors prove it), but validates current approach.

## Structured Deliberation

| Hypothesis | Strengths | Weaknesses | Key Uncertainty | Information Gain |
|------------|-----------|------------|-----------------|-----------------|
| H1: Extend Tier-0 + local model | Direct token reduction, proven by competitors | Adds Docker image size (~1.12 GB for local model), latency for local inference | How many eval tasks are coverable by local models? | High — directly measurable as % zero-token tasks |
| H2: Prompt caching | Free savings, zero code change, no competitor doing it | Benefit depends on eval prompt structure (unknown until launch day) | Will judge prompts share common prefixes? | Low risk, medium potential — easy to implement, measure on our sample |
| H3: Single escalation | Already implemented, proven optimal | — | Confirms current approach | Low (already decided) |

## Selected Direction

- **Chosen hypothesis**: H1 (Extend Tier 0 + local model) as primary for highest token reduction impact. H2 (prompt caching) as secondary for free additional savings.
- **Rationale**: H1 directly addresses our biggest gap vs competitors. SebAustin achieves 32.5% zero-token tasks through extended Tier-0 solvers; realjunjiejj achieves additional savings through local model inference. Without this, we cannot match their token efficiency. H2 is free — restructure prompts with common prefixes, get up to 50% discount on input tokens with zero code change.
- **Key risks**: Local model adds 1.12 GB to Docker image (must stay under 10 GB limit). Inference latency on 2 vCPUs may add 1-3s per task. Model may produce wrong answers for out-of-distribution tasks — needs conservative gating.
- **Pre-specified success criteria**: At least 25% of evaluation tasks handled at zero Fireworks tokens (Tier-0 + local model). At least 15% measurable prompt cache hit rate.
- **Fallback plan**: If local model integration fails (time, correctness, Docker size), extend only Tier-0 solvers (no local model). This still improves zero-token coverage but less dramatically.

## Action Items

1. Extend Tier-0 solvers: date math (python-dateutil), string ops (regex), unit conversion (pint), simple arithmetic word problems
2. Add local model: Integrate llama.cpp with Qwen2.5 1.5B GGUF for constrained tasks (sentiment, NER, constrained summarization)
3. Restructure prompts for caching: common prefix format across all system prompts
4. Keep Single-escalation policy (current approach is optimal per competitor evidence)
5. Target: 30%+ zero-token tasks, exploit prompt caching, maintain 95%+ accuracy gate
