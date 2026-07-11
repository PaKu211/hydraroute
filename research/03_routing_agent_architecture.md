# Token-Efficient Routing Agent - Architecture Research

## Core Concept: Multi-Model Routing
The most effective way to reduce costs is to ensure every request is handled by the "cheapest capable model."

## Three-Tier Architecture

### Tier 0: Zero-Cost Execution (No LLM needed)
- Pattern matching: Regex, string operations
- Calculations: Math, unit conversions (use Python eval)
- Lookups: Known facts, static data
- Token cost: 0
- Examples: "What is 2+2?", "Convert 100 USD to EUR", simple factual queries

### Tier 1: Small/Fast Model (Minimal tokens)
- Model: Smallest allowed model (e.g., Llama 3B or 8B via Fireworks)
- Tasks: Simple Q&A, classification, extraction, summarization
- Token cost: Low
- Strategy: Concise system prompts, minimal context

### Tier 2: Large/Reasoning Model (When absolutely needed)
- Model: Largest allowed model (e.g., Llama 70B, Qwen 72B, DeepSeek)
- Tasks: Complex reasoning, multi-step logic, nuanced analysis
- Token cost: Higher but justified
- Strategy: Only used when task is pre-classified as complex

## Task Category → Tier Mapping
1. factual_knowledge → Tier 1 (small model sufficient)
2. math → Tier 0 (Python eval) with Tier 1 fallback
3. sentiment_classification → Tier 1 (simple classification)
4. text_summarization → Tier 1 (8B models handle well)
5. ner → Tier 1 (extraction task)
6. code_debugging → Tier 2 (complex reasoning needed)
7. logical_reasoning → Tier 2 (multi-step reasoning)
8. code_generation → Tier 1 for simple, Tier 2 for complex

## Token Optimization Strategies

### 1. Prompt Compression
- Minimal system prompts per tier
- No unnecessary context
- Direct instruction format
- Category-specific max_tokens caps

### 2. Math Execution Locally
- Parse mathematical expressions
- Use Python's eval/sympy
- Zero tokens consumed

### 3. Strict Output Budgeting
- sentiment_classification: max_tokens=50
- factual_knowledge: max_tokens=200
- code_generation: max_tokens=500
- text_summarization: max_tokens=300

### 4. Semantic Caching
- Hash prompts to serve cached responses for duplicates
- Won't help in competition (unique tasks) but good practice

## Winning Reference Projects
- TERA: Four-layer optimization with Zero-Token Rule Engine
- SplitLLM: Explainable hybrid routing + multi-stage reasoning
- Token-Slasher: Minimal orchestration, forces deterministic output

## Critical Success Factors
1. PASS the accuracy gate first (no point saving tokens if answers are wrong)
2. Minimize tokens ONLY after ensuring accuracy
3. Use the smallest model in ALLOWED_MODELS for simple tasks
4. Use Python execution for ALL math tasks
5. Keep system prompts under 50 tokens
6. Set strict max_tokens per category
7. Handle errors gracefully - fallback to bigger model if small fails
