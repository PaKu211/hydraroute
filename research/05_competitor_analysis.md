# Competitor Analysis - AMD Hackathon ACT II

## TERA (Token-Efficient Routing Agent) - Adeel-x
The strongest known competitor. Architecture:

### 6-Rung Escalation Ladder
- Rung 0: Semantic cache (SQLite + MiniLM), deterministic Python for math
- Rungs 1-3: LOCAL model inference (Gemma 3 / Qwen3 via llama.cpp) with:
  - Self-consistency majority voting
  - Confidence gating via llama.cpp logprobs
- Rung 4: "1-token" YES/NO verification call to cheap remote model
- Rungs 5-6: Paid remote Fireworks models with compressed prompts

### Key Differentiators vs. HydraRoute current version
1. LOCAL model inference (Gemma/Qwen via llama.cpp) - 0 token cost for medium tasks
2. Confidence gating using logprobs - knows when to escalate
3. Semantic caching with SQLite + MiniLM
4. "1-token judge" verification call

## Other Notable Submissions
- max_tokens=4 for sentiment (just "POS", "NEG", "NEU" + 1 token)
- ThreadPoolExecutor for concurrent task processing
- "Disabling thinking" in reasoning models to avoid billed reasoning tokens
- SHA1-keyed in-memory cache
- JSON forced outputs for structured tasks
- Syntax tree parsing for math
- Regex classifiers for categories

## What We Must Add to Beat Them
1. **Concurrency**: ThreadPoolExecutor/asyncio for parallel task processing
2. **Ultra-short outputs**: sentiment max_tokens=4, NER as JSON max_tokens=100
3. **In-memory SHA1 cache**: Hash instruction text, serve cached answers
4. **Thinking=disabled**: For any model that supports thinking parameter
5. **Better math parsing**: Syntax tree approach, not just regex
6. **Retry with exponential backoff**: Don't give up on API errors
7. **Model health check at startup**: Verify which models work before processing

## Token Savings Quantified
- Sentiment with max_tokens=4 vs 50 = 12x savings on output tokens
- Caching 20% of duplicate tasks = 20% fewer API calls
- Concurrency: Complete all tasks before timeout hits
- Disabled thinking: Save 100-2000 reasoning tokens per call

## Winning Insight
"The winning mindset focused on NOT CALLING THE API AT ALL"
- Free local: math, deterministic patterns = 0 tokens
- Cache hit: duplicate prompts = 0 tokens  
- Tiny models + tiny outputs: simple tasks = minimal tokens
- Only use large models for true reasoning tasks
