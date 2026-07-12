# Research State: HydraRoute — Hybrid Token-Efficient Routing Agent

## Current Stage
SCOPE → LITERATURE (completed) → REASON (completed)

## Research Question
How can we design a state-of-the-art hybrid token-efficient routing agent that wins the AMD Developer Hackathon ACT II Track 1?

## Key Decisions
- [SCOPE]: Deep research requested — comprehensive literature, competitor, and platform analysis executed
- [LITERATURE]: 4 parallel research agents completed — academic papers, hackathon winners, GitHub repos, Fireworks AI features
- [REASON]: Selected direction — extend Tier-0 solvers (date, string, unit) + add local llama.cpp model + exploit Fireworks prompt caching

## Experiment Log
| Attempt | Method | Result | Status |
|---------|--------|--------|--------|

## Critique History
- (none yet — pending methodology.md)

## What Worked
- Parallel research agents: all 4 returned comprehensive findings
- Verified 2 strongest competitors: SebAustin (99.5% acc, 32.5% zero-token) and realjunjiejj (local 1.5B Qwen)
- Fireworks prompt caching: 50% discount, no code change needed, no competitor exploiting it

## What Didn't Work
- Atlas graph init: "unauthenticated" — user not logged into OpenScience CLI
- Some competitor GitHub repos returned 404 (private repos or renamed)

## Open Questions
- What is the exact distribution of task categories in the hidden evaluation set?
- Will the evaluation prompts share common prefixes (for caching optimization)?
- Can a 1.12 GB local model fit alongside Tier-0 solvers within the 4 GB RAM / 10 GB Docker limit?

## Artifacts
- literature-review.md: ✅ completed (comprehensive synthesis across 4 facets, 10+ verified papers)
- reasoning.md: ✅ completed (selected H1: extended Tier 0 + local model + prompt caching)
- methodology.md: ❌ (next step)
