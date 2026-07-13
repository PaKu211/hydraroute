# Research Deliberation: Routing Overhead & Escalation Misconfiguration in Hybrid LLM Routers

## Knowledge Consolidation

From the literature (47 papers + 3 deep-research facets, all verified):
1. **LLM routing is mature in theory, noisy in practice.** FrugalGPT, RouteLLM, MixLLM,
   AutoMix, HybridLLM dominate a single fixed model *only when the price gap is large and
   routing is accurate*. **RouterBench's central finding**: a *learned* router generally
   does NOT dominate a simple single-model baseline; savings are acute-sensitive to the
   assumed price gap (Hu et al. 2024).
2. **Token-cutting ≠ call-skipping.** LLMLingua, Selective Context, LongLLMLingua,
   Scissorhands compress *tokens*; FrugalGPT/MixLLM/RouteLLM choose a *cheaper LLM*. **No
   prior work skips the LLM entirely via deterministic free solvers** (regex/lookup/
   arithmetic) as a pre-routing Tier-0. This is HydraRoute's novelty.
3. **Evaluation rigor matters.** Gudibande et al. warn that proxy-metric gains fail to
   generalize; RouterBench mandates fixed-pricing, multi-regime cost reporting.

## Knowledge Gaps & Contradictions
- **Gap**: Deterministic Tier-0 offload (free, zero-token) is unexplored; the field assumes
  *every* query touches an LLM.
- **Contradiction with initial assumption**: We assumed a hybrid router is *always* cheaper
  than always-large. Measured data **refutes** this: a naive category→size mapping
  *over-escalates* and costs **+51% vs always-large** at actual Gemma-4 pricing. This is a
  concrete instance of RouterBench's "learned/simple router can lose" warning — here caused
  by misconfiguration, not learning.
- **Resolution**: A *data-driven* fix (Tier-0 deterministic offload + ablated escalation,
  escalates only `sentiment_classification`) restores the saving and makes the router
  robust, unlike a learned router whose error variance it avoids.

## Candidate Hypotheses
### H1 (CONFIRMED, negative): Naive hybrid routing can cost MORE than always-large
- Evidence: E1 config A (pre-fix mapping) → +51% tokens/cost vs always-large at Gemma-4
  pricing; only 9/45 paid tasks needed large. The over-escalation is the mechanism.
- Significance: concrete, reproducible counterexample to "routing always saves."

### H2 (CONFIRMED, positive): Deterministic Tier-0 + ablated escalation restores the saving
- Evidence: data-driven fix routes only `sentiment_classification`→large (9 tasks), 22 tasks
  solved at Tier-0 (zero token), 65/67 pass. At frontier pricing this is ~92% cheaper than
  always-large.
- Significance: Tier-0 offload is more robust than learned routing under small price gaps.

### H3 (in progress): The effect generalizes across model families
- E1 to be repeated on a 2nd family (Llama-3.1-8B small / 70B large; Qwen2.5-7B/32B).
- E3 serving-speed gap measured on local vLLM (small model ~2× faster → routing feasible).

## Structured Deliberation
| Hypothesis | Strengths | Weaknesses | Info Gain |
|------------|-----------|------------|-----------|
| H1 (naive router costs more) | Real measured data | only 1 family done | HIGH (negative result) |
| H2 (fix restores saving) | Real measured data | depends on task mix | HIGH |
| H3 (generalizes) | strengthens claim | blocked on OpenRouter credit for 2nd routing family | MEDIUM (pending) |

## Selected Direction
**Chosen**: ONE honest empirical arc — *build → measure → diagnose → fix → report.*
Title: "Routing Overhead and Escalation Misconfiguration in Hybrid LLM Routers: An
Empirical Study with a Data-Driven Fix."

**Rationale**: The negative result (H1) is the scientifically interesting contribution; the
fix (H2) shows the remedy; multi-family (H3) and E3 (serving feasibility) broaden it. This
matches Efficient-LLM Workshop / ACL System Demo expectations for honest empirical work.

**Pre-specified success criteria** (honest):
1. Report real per-task cost under two pricing regimes (actual Gemma-4, frontier gap).
2. Demonstrate the over-escalation mechanism with per-task route attribution.
3. Show the data-driven fix yields a real (not assumed) saving.
4. Validate the small-model serving gap (E3) so routing latency is feasible.

**Fallback**: If H3 (2nd family) cannot complete due to API credit, report 1 family
honestly + note generalization as future work; the core negative+fix result stands on its
own.
