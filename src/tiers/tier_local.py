"""
Tier Local - Zero-token local inference via llama.cpp subprocess + GGUF model.
Downloads model lazily on first use (not at Docker build time) to keep image small.
"""

import logging
import os
import subprocess
import tempfile

logger = logging.getLogger("hydraroute")

MODEL_PATH = os.environ.get(
    "LOCAL_MODEL_PATH", "/app/models/qwen2.5-1.5b-instruct-q4_k_m.gguf"
)
LLAMA_LIB_DIR = os.environ.get("LLAMA_LIB_DIR", "/app/bin/llama-b9969")
LLAMA_CLI = os.environ.get("LLAMA_CLI_PATH", os.path.join(LLAMA_LIB_DIR, "llama-cli"))
GGUF_REPO = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
GGUF_FILE = "qwen2.5-1.5b-instruct-q4_k_m.gguf"

_llama_available = None


def _try_download():
    if os.path.exists(MODEL_PATH):
        return True
    try:
        from huggingface_hub import hf_hub_download

        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        logger.info("Downloading GGUF model (~1GB, first use only)...")
        hf_hub_download(
            repo_id=GGUF_REPO, filename=GGUF_FILE, local_dir=os.path.dirname(MODEL_PATH)
        )
        logger.info("GGUF model ready")
        return True
    except Exception as e:
        logger.warning("GGUF download failed: %s — API fallback", e)
        return False


def _is_available() -> bool:
    global _llama_available
    if _llama_available is not None:
        return _llama_available
    bin_ok = os.path.exists(LLAMA_CLI)
    model_ok = os.path.exists(MODEL_PATH) or _try_download()
    _llama_available = bin_ok and model_ok
    if not _llama_available:
        logger.debug(
            "Tier Local unavailable: model=%s exists=%s, llama-cli=%s exists=%s",
            MODEL_PATH,
            os.path.exists(MODEL_PATH),
            LLAMA_CLI,
            os.path.exists(LLAMA_CLI),
        )
    return _llama_available


def execute(instruction: str, category: str = "") -> str | None:
    if not _is_available():
        return None

    if category not in (
        "sentiment_classification",
        "ner",
        "named_entity_recognition",
        "factual_knowledge",
        "text_summarization",
    ):
        return None

    prompts = {
        "sentiment_classification": (
            f"<|im_start|>system\nClassify sentiment. Reply POS, NEG, or NEU.<|im_end|>\n"
            f"<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n"
        ),
        "ner": (
            f"<|im_start|>system\nExtract named entities as JSON.<|im_end|>\n"
            f"<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n"
        ),
        "named_entity_recognition": (
            f"<|im_start|>system\nExtract named entities as JSON.<|im_end|>\n"
            f"<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n"
        ),
        "factual_knowledge": (
            f"<|im_start|>system\nAnswer concisely.<|im_end|>\n"
            f"<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n"
        ),
        "text_summarization": (
            f"<|im_start|>system\nSummarize concisely.<|im_end|>\n"
            f"<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n"
        ),
    }

    prompt = prompts.get(category)
    if not prompt:
        return None

    try:
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = LLAMA_LIB_DIR + ":" + env.get("LD_LIBRARY_PATH", "")
        result = subprocess.run(
            [
                LLAMA_CLI,
                "-m",
                MODEL_PATH,
                "--prompt",
                prompt,
                "-n",
                "150",
                "-t",
                "2",
                "--temp",
                "0.0",
                "--no-display-prompt",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )
        output = result.stdout.strip()
        if output:
            cleaned = output.split("<|im_end|>")[0].strip()
            logger.info("Tier Local solved [%s]: %s", category, cleaned[:60])
            return cleaned
    except subprocess.TimeoutExpired:
        logger.warning("Tier Local timed out for [%s]", category)
    except Exception as e:
        logger.warning("Tier Local failed [%s]: %s", category, e)

    return None
