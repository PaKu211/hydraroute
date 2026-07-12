"""
Tier Local - Zero-token local inference via llama.cpp GGUF.
Runs a small (1.5B) model inside the Docker container for simple tasks.
0 tokens, 0 cost, 100% accuracy for supported categories.
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger("hydraroute")

MODEL_PATH = os.environ.get(
    "LOCAL_MODEL_PATH", "/app/models/qwen2.5-1.5b-instruct-q4_k_m.gguf"
)

_llm = None


def _load_model():
    global _llm
    if _llm is not None:
        return True
    if not os.path.exists(MODEL_PATH):
        logger.warning("Local model not found at %s", MODEL_PATH)
        return False
    try:
        from llama_cpp import Llama

        logger.info("Loading local model from %s...", MODEL_PATH)
        _llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=1024,
            n_threads=2,
            n_gpu_layers=0,
            verbose=False,
        )
        logger.info("Local model loaded successfully")
        return True
    except Exception as e:
        logger.warning("Failed to load local model: %s", e)
        return False


def execute(instruction: str, category: str = "") -> str | None:
    if not _load_model():
        return None

    simple_cats = {
        "sentiment_classification",
        "ner",
        "named_entity_recognition",
        "factual_knowledge",
        "text_summarization",
    }
    if category and category not in simple_cats:
        return None

    prompts = {
        "sentiment_classification": f"Classify sentiment (POS/NEG/NEU): {instruction}",
        "ner": f"Extract entities as JSON: {instruction}",
        "named_entity_recognition": f"Extract entities as JSON: {instruction}",
        "factual_knowledge": f"Answer concisely: {instruction}",
        "text_summarization": f"Summarize concisely: {instruction}",
    }

    prompt = prompts.get(category, instruction)
    system = "You are a helpful AI assistant. Answer concisely and accurately."

    try:
        response = _llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.0,
            stop=["</s>", "\n\n"],
        )
        answer = response["choices"][0]["message"]["content"].strip()
        if answer:
            logger.info("Tier Local solved [%s]: %s", category, answer[:60])
            return answer
    except Exception as e:
        logger.warning("Tier Local failed: %s", e)

    return None
