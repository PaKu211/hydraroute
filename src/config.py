"""
Configuration module for HydraRoute Agent.
Reads environment variables and configures the routing system.
"""

import os
import logging
from dataclasses import dataclass, field

logger = logging.getLogger("hydraroute")


@dataclass
class Config:
    """Runtime configuration loaded from environment variables."""

    fireworks_api_key: str = ""
    fireworks_base_url: str = "https://api.fireworks.ai/inference/v1"
    allowed_models: list[str] = field(default_factory=list)
    input_path: str = "/input/tasks.json"
    output_path: str = "/output/results.json"

    # Model tier assignments (populated at runtime from ALLOWED_MODELS)
    small_model: str = ""
    large_model: str = ""

    # Known model size rankings (smallest to largest)
    MODEL_SIZE_ORDER: dict[str, int] = field(default_factory=lambda: {
        "llama-v3p2-1b-instruct": 1,
        "llama-v3p2-3b-instruct": 3,
        "mistral-7b-instruct": 7,
        "llama-v3-8b-instruct": 8,
        "llama-v3p1-8b-instruct": 8,
        "deepseek-v4-flash": 20,
        "llama-v3p1-70b-instruct": 70,
        "llama-v3p3-70b-instruct": 70,
        "qwen2p5-72b-instruct": 72,
        "deepseek-v3": 671,
        "deepseek-r1": 671,
        "qwen3-235b-a22b": 235,
        "deepseek-v4-pro": 700,
    })

    def __post_init__(self):
        self._load_from_env()

    def _load_from_env(self):
        """Load configuration from environment variables."""
        self.fireworks_api_key = os.environ.get("FIREWORKS_API_KEY", "")
        self.fireworks_base_url = os.environ.get(
            "FIREWORKS_BASE_URL",
            "https://api.fireworks.ai/inference/v1"
        )

        # Parse ALLOWED_MODELS - comma-separated list
        models_str = os.environ.get("ALLOWED_MODELS", "")
        if models_str:
            self.allowed_models = [
                m.strip() for m in models_str.split(",") if m.strip()
            ]
        else:
            self.allowed_models = []

        # Detect and set adaptive paths
        self.input_path = os.environ.get("INPUT_PATH", "/input/tasks.json")
        if not os.path.exists(os.path.dirname(self.input_path)) or not os.access(os.path.dirname(self.input_path), os.R_OK):
            self.input_path = "./input/tasks.json"

        self.output_path = os.environ.get("OUTPUT_PATH", "/output/results.json")
        out_dir = os.path.dirname(self.output_path)
        try:
            if not os.path.exists(out_dir):
                os.makedirs(out_dir, exist_ok=True)
            # Test writability of output directory
            test_file = os.path.join(out_dir, ".write_test")
            with open(test_file, "w") as f:
                f.write("")
            os.remove(test_file)
        except (OSError, IOError):
            self.output_path = "./output/results.json"
            os.makedirs("./output", exist_ok=True)

        # Auto-assign small and large models based on size
        self._assign_model_tiers()

        logger.info(
            "Config loaded: %d models available, small=%s, large=%s",
            len(self.allowed_models),
            self.small_model,
            self.large_model,
        )

    def _get_model_size(self, model_id: str) -> int:
        """Get estimated model size in billions of parameters."""
        # Extract the model name from full ID
        # e.g., "accounts/fireworks/models/llama-v3p1-8b-instruct" -> "llama-v3p1-8b-instruct"
        name = model_id.split("/")[-1] if "/" in model_id else model_id

        # Check known sizes
        for key, size in self.MODEL_SIZE_ORDER.items():
            if key in name:
                return size

        # Try to extract size from name (e.g., "70b", "8b")
        import re
        match = re.search(r"(\d+)b", name.lower())
        if match:
            return int(match.group(1))

        # Default: treat as medium
        return 50

    def _assign_model_tiers(self):
        """Assign models to tiers based on their size."""
        if not self.allowed_models:
            return

        # Sort models by size
        sorted_models = sorted(
            self.allowed_models,
            key=lambda m: self._get_model_size(m)
        )

        # Smallest = Tier 1, Largest = Tier 2
        self.small_model = sorted_models[0]
        self.large_model = sorted_models[-1]

        # If only one model available, use it for both tiers
        if len(sorted_models) == 1:
            self.large_model = sorted_models[0]

        logger.info(
            "Model tiers: small=%s (size=%d), large=%s (size=%d)",
            self.small_model,
            self._get_model_size(self.small_model),
            self.large_model,
            self._get_model_size(self.large_model),
        )


# Category-specific configurations
# Optimized for minimum token usage while maintaining accuracy
CATEGORY_CONFIG = {
    "factual_knowledge": {
        "tier": 1,
        "system_prompt": "Answer factually and concisely. No explanations.",
        "max_tokens": 200,
        "temperature": 0.1,
    },
    "math": {
        "tier": 0,  # Zero-cost: Python execution
        "system_prompt": "Solve this and output only the final numerical answer.",
        "max_tokens": 150,
        "temperature": 0.0,
    },
    "mathematical_reasoning": {
        "tier": 0,
        "system_prompt": "Solve this and output only the final numerical answer.",
        "max_tokens": 150,
        "temperature": 0.0,
    },
    "sentiment_classification": {
        "tier": 1,
        "system_prompt": "Classify: POS, NEG, or NEU.",
        "max_tokens": 4,  # Just POS/NEG/NEU + buffer = maximum savings
        "temperature": 0.0,
    },
    "text_summarization": {
        "tier": 1,
        "system_prompt": "Summarize this text concisely.",
        "max_tokens": 300,
        "temperature": 0.3,
    },
    "ner": {
        "tier": 1,
        "system_prompt": "Extract named entities as JSON.",
        "max_tokens": 150,
        "temperature": 0.0,
    },
    "named_entity_recognition": {
        "tier": 1,
        "system_prompt": "Extract named entities as JSON.",
        "max_tokens": 150,
        "temperature": 0.0,
    },
    "code_debugging": {
        "tier": 2,
        "system_prompt": "Fix this code. Output only the corrected code.",
        "max_tokens": 500,
        "temperature": 0.1,
    },
    "logical_reasoning": {
        "tier": 2,
        "system_prompt": "Solve step-by-step, ending with the final conclusion.",
        "max_tokens": 500,
        "temperature": 0.1,
    },
    "deductive_reasoning": {
        "tier": 2,
        "system_prompt": "Solve step-by-step, ending with the final conclusion.",
        "max_tokens": 500,
        "temperature": 0.1,
    },
    "code_generation": {
        "tier": 2,  # Code gen needs quality - use large model directly
        "system_prompt": "Write code to solve this. No explanations.",
        "max_tokens": 500,
        "temperature": 0.1,
    },
}

# Default config for unknown categories
DEFAULT_CATEGORY_CONFIG = {
    "tier": 1,
    "system_prompt": "Answer the following question concisely and accurately.",
    "max_tokens": 300,
    "temperature": 0.2,
    "fallback_tier": 2,
}
