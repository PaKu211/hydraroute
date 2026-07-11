"""
Router module for HydraRoute Agent.
Determines which tier to use for each task and implements fallback chains.
"""

import logging

from openai import OpenAI

from src.config import Config, CATEGORY_CONFIG, DEFAULT_CATEGORY_CONFIG
from src.token_tracker import TokenTracker
from src.tiers import tier_zero, tier_one, tier_two

logger = logging.getLogger("hydraroute")

# Map category name variations to canonical names
CATEGORY_ALIASES: dict[str, str] = {
    "math": "math",
    "mathematical_reasoning": "mathematical_reasoning",
    "maths": "math",
    "arithmetic": "math",
    "sentiment": "sentiment_classification",
    "sentiment_classification": "sentiment_classification",
    "sentiment_analysis": "sentiment_classification",
    "summarization": "text_summarization",
    "text_summarization": "text_summarization",
    "summary": "text_summarization",
    "ner": "ner",
    "named_entity_recognition": "named_entity_recognition",
    "entity_recognition": "ner",
    "factual_knowledge": "factual_knowledge",
    "factual": "factual_knowledge",
    "knowledge": "factual_knowledge",
    "code_debugging": "code_debugging",
    "debugging": "code_debugging",
    "debug": "code_debugging",
    "logical_reasoning": "logical_reasoning",
    "deductive_reasoning": "deductive_reasoning",
    "reasoning": "logical_reasoning",
    "logic": "logical_reasoning",
    "code_generation": "code_generation",
    "code_gen": "code_generation",
    "coding": "code_generation",
}


def normalize_category(category: str) -> str:
    """Normalize category name to match CATEGORY_CONFIG keys."""
    cat = category.strip().lower().replace("-", "_").replace(" ", "_")

    # Check aliases
    if cat in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[cat]

    # Check if it directly matches a config key
    if cat in CATEGORY_CONFIG:
        return cat

    # Fuzzy match: check if any config key is contained in the category
    for key in CATEGORY_CONFIG:
        if key in cat or cat in key:
            return key

    logger.warning("Unknown category '%s', using default config", category)
    return cat


def get_category_config(category: str) -> dict:
    """Get the configuration for a normalized category."""
    normalized = normalize_category(category)
    return CATEGORY_CONFIG.get(normalized, DEFAULT_CATEGORY_CONFIG)


def route_task(
    task: dict,
    config: Config,
    client: OpenAI,
) -> str:
    """Route a single task to the appropriate tier and return the answer.

    Implements fallback chain:
        Tier 0 (local) -> Tier 1 (small model) -> Tier 2 (large model)

    Args:
        task: Task dict with task_id, category, instruction.
        config: Runtime configuration with model assignments.
        client: OpenAI-compatible client for API calls.

    Returns:
        Answer string. Never returns None - falls back to error message.
    """
    task_id = task["task_id"]
    category = task["category"]
    instruction = task["instruction"]

    cat_config = get_category_config(category)
    target_tier = cat_config.get("tier", 1)

    logger.info(
        "Routing task %s [%s] -> tier %d", task_id, category, target_tier
    )

    answer: str | None = None

    # ── Tier 0: Local execution (math) ──
    if target_tier == 0:
        try:
            answer = tier_zero.execute(instruction)
            if answer is not None:
                TokenTracker().record_tier_zero()
                logger.info("Task %s solved by Tier 0", task_id)
                return answer
        except Exception as e:
            logger.warning("Tier 0 failed for task %s: %s", task_id, e)

        # Fallback: Tier 0 -> Tier 1
        logger.info("Tier 0 fallback -> Tier 1 for task %s", task_id)
        # Use math-specific config for the API call
        math_api_config = {
            "system_prompt": "Solve this math problem. Give only the final answer.",
            "max_tokens": cat_config.get("max_tokens", 150),
            "temperature": 0.0,
        }
        target_tier = 1
        cat_config = math_api_config

    # ── Tier 1: Small model ──
    if target_tier <= 1 and config.small_model:
        try:
            answer = tier_one.execute(
                client=client,
                model=config.small_model,
                instruction=instruction,
                category=category,
                category_config=cat_config,
                task_id=task_id,
            )
            if answer:
                return answer
        except Exception as e:
            logger.warning("Tier 1 failed for task %s: %s", task_id, e)

        # Fallback: Tier 1 -> Tier 2
        logger.info("Tier 1 fallback -> Tier 2 for task %s", task_id)

    # ── Tier 2: Large model ──
    if config.large_model:
        try:
            # For Tier 2 fallbacks, use the original category config if available
            t2_config = CATEGORY_CONFIG.get(
                normalize_category(category), cat_config
            )
            answer = tier_two.execute(
                client=client,
                model=config.large_model,
                instruction=instruction,
                category=category,
                category_config=t2_config,
                task_id=task_id,
            )
            if answer:
                return answer
        except Exception as e:
            logger.error("Tier 2 failed for task %s: %s", task_id, e)

    # ── All tiers exhausted ──
    logger.error("All tiers failed for task %s", task_id)
    return "I could not determine the answer."
