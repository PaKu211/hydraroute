"""
Tier 1 - Small model execution with exponential backoff.
Uses the smallest available model via Fireworks AI API (OpenAI-compatible).
Optimized for simple tasks: factual knowledge, sentiment, NER, summarization.
"""

import logging
import time

from openai import OpenAI, RateLimitError, APIError

from src.token_tracker import TokenTracker

logger = logging.getLogger("hydraroute")

MAX_RETRIES = 3
BACKOFF_BASE = 1.5  # seconds


def execute(
    client: OpenAI,
    model: str,
    instruction: str,
    category: str,
    category_config: dict,
    task_id: str = "",
) -> str | None:
    """Execute a task using the small (Tier 1) model with retry + backoff.

    Args:
        client: OpenAI-compatible client configured for Fireworks.
        model: Model ID to use.
        instruction: The task instruction.
        category: Task category name.
        category_config: Dict with system_prompt, max_tokens, temperature.
        task_id: Task ID for token tracking.

    Returns:
        Answer string, or None if all retries fail.
    """
    system_prompt = category_config.get("system_prompt", "Answer concisely.")
    max_tokens = category_config.get("max_tokens", 200)
    temperature = category_config.get("temperature", 0.1)

    logger.info(
        "Tier 1 [%s] task=%s model=%s max_tokens=%d",
        category, task_id, model.split("/")[-1], max_tokens,
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Build request params - disable thinking if supported
            model_lower = model.lower()
            extra_params: dict = {}
            if any(m in model_lower for m in ["deepseek", "qwen"]):
                # Disable thinking/reasoning to save tokens
                extra_params["extra_body"] = {"thinking": {"type": "disabled"}}

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": instruction},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                **extra_params,
            )

            answer = response.choices[0].message.content
            if answer:
                answer = answer.strip()

            # Track tokens
            usage = response.usage
            if usage:
                TokenTracker().record(
                    task_id=task_id,
                    model=model,
                    prompt_tokens=usage.prompt_tokens or 0,
                    completion_tokens=usage.completion_tokens or 0,
                )

            logger.debug("Tier 1 answer[:100]: %s", (answer or "")[:100])
            return answer

        except RateLimitError as e:
            wait = BACKOFF_BASE ** attempt
            logger.warning(
                "Tier 1 rate limit (attempt %d/%d) for task %s, retrying in %.1fs: %s",
                attempt, MAX_RETRIES, task_id, wait, e,
            )
            time.sleep(wait)
        except APIError as e:
            logger.error("Tier 1 API error for task %s: %s", task_id, e)
            if attempt < MAX_RETRIES:
                time.sleep(BACKOFF_BASE)
            else:
                return None
        except Exception as e:
            logger.error("Tier 1 unexpected error for task %s: %s", task_id, e)
            return None

    logger.error("Tier 1 exhausted all %d retries for task %s", MAX_RETRIES, task_id)
    return None
