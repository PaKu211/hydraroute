"""
Token Compression module for HydraRoute Agent (v3).
Implements Lite, Caveman, and Headroom prompt compression algorithms to slash token counts.
Safe, category-aware prompt optimization.
"""

import json
import logging
import re
from typing import Any, Union

logger = logging.getLogger("hydraroute.compression")

# Caveman stop words (safe fillers to drop for simple tasks)
CAVEMAN_STOPWORDS = {
    "a", "an", "the", "and", "but", "or", "because", "as", "until", "while",
    "of", "at", "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "to", "from",
    "up", "down", "in", "out", "on", "off", "over", "under", "again", "further",
    "then", "once", "here", "there", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "only", "own", "same", "so", "than", "too", "very", "can", "will", "just",
    "should", "now", "please", "could", "would", "tell", "show", "give", "write",
    "calculate", "compute", "evaluate", "solve", "find", "you", "me", "what", "is",
    "it", "he", "she", "they", "we", "i", "my", "your", "his", "her", "their", "our",
    "us", "be", "been", "being", "have", "has", "had", "do", "does", "did", "doing",
    "are", "was", "were", "am"
}


class PromptCompressor:
    """Handles token saving operations on input instructions."""

    def __init__(self):
        pass

    def compress_lite(self, text: str) -> str:
        """[Lite] Cleanup redundant whitespaces, newlines, and tabs."""
        if not text:
            return ""
        # Replace multiple spaces/tabs/newlines with a single space
        return re.sub(r"\s+", " ", text).strip()

    def compress_caveman(self, text: str) -> str:
        """[Caveman] Removes safe filler words/stopwords.

        Only apply to textual facts and summarizations where grammar doesn't impact accuracy.
        """
        if not text:
            return ""
        words = text.split()
        # Keep words that are not in the caveman stopwords list
        filtered = [w for w in words if w.lower().strip("?,.") not in CAVEMAN_STOPWORDS]
        # Reconstruct and return (ensure it still has some text)
        result = " ".join(filtered)
        return result if result else text

    def compress_headroom(self, data: Union[str, dict, list]) -> str:
        """[Headroom] Minimizes JSON payload by stripping spaces around delimiters."""
        if isinstance(data, (dict, list)):
            return json.dumps(data, separators=(",", ":"))
        if isinstance(data, str):
            try:
                # If it's a valid JSON string, minify it
                parsed = json.loads(data)
                return json.dumps(parsed, separators=(",", ":"))
            except json.JSONDecodeError:
                # Not a JSON string, return as is
                return data
        return str(data)

    def optimize(self, instruction: str, category: str) -> str:
        """Orchestrate compression safely based on task category.

        Args:
            instruction: The original task instruction.
            category: Canonical category name.

        Returns:
            Optimized, token-compressed prompt string.
        """
        original_len = len(instruction)

        # 1. Clean format (Lite) - Always safe
        compressed = self.compress_lite(instruction)

        # 2. Heuristic prose pruning (Caveman) - Safe only for simple NLP tasks
        # DO NOT run on code, math, or logic where keywords are syntax-critical
        if category in ("factual_knowledge", "text_summarization", "sentiment_classification"):
            compressed = self.compress_caveman(compressed)

        compressed_len = len(compressed)
        saving_pct = ((original_len - compressed_len) / original_len * 100) if original_len > 0 else 0
        if saving_pct > 5:
            logger.info(
                "Prompt compressed (category [%s]): %d -> %d chars (-%.1f%%)",
                category, original_len, compressed_len, saving_pct
            )

        return compressed
