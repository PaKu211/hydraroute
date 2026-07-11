# HydraRoute - NotebookLM Risk Analysis & Mitigations

## Risk 1: Docker Container Failures
- **Architecture mismatch**: Always build with `docker build --platform linux/amd64`
- **Exit code**: Wrap entire task loop in try/except, always exit(0)
- **Hardcoded credentials**: Use os.getenv() strictly, never hardcode

## Risk 2: Edge Cases Per Category
- **sentiment/ner**: Model gives conversational text instead of structured output
  - Mitigation: Low temperature (0.0-0.3), strict system prompts
- **code_generation**: Output exceeds max_tokens, code gets truncated
  - Mitigation: Check finish_reason, fallback with higher max_tokens
- **All categories**: Unicode/unexpected input format
  - Mitigation: String sanitization before prompting

## Risk 3: Single Model in ALLOWED_MODELS
- If only 1 model, assign it to BOTH Tier 1 and Tier 2
- Router should not crash, just route everything to same model

## Risk 4: Math Word Problems (not equations)
- eval()/sympy can only handle pure math expressions
- Wrap Tier 0 in try/except, fallback to Tier 1 for word problems
- This is CRITICAL - many math tasks will be word problems

## Risk 5: Timeout (~30s per task, ~10min total)
- Use signal/threading timeout (25s safety margin)
- If API call exceeds 25s, abort and use simplified prompt on small model
- Avoid excessive Tier 2 calls

## Risk 6: API Rate Limiting (HTTP 429)
- Implement exponential backoff (1s, 2s, 4s)
- After 3 retries, try different model from ALLOWED_MODELS
- Sequential processing (not parallel) to avoid rate limits

## Additional Risk: Invalid JSON Output
- Always write atomically (write to temp file, rename)
- Validate JSON before writing
- If all tasks fail, still write empty array []
