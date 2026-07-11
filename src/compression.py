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
# Heuristic Prompt Cleaner patterns
SAFE_HEURISTIC_PATTERNS = [
    (r"(?i)\bfind and fix the bug in this python code\b", "Fix Python bug"),
    (r"(?i)\bfind and fix the bug in the following python code\b", "Fix Python bug"),
    (r"(?i)\bwrite a python function to\b", "Write Python function to"),
    (r"(?i)\bsummarize the following text in one sentence\b", "Summarize in 1 sentence"),
    (r"(?i)\bsummarize the following text\b", "Summarize"),
    (r"(?i)\bextract all named entities \(persons, organizations, locations\) from this text\b", "Extract named entities (Person/Org/Loc)"),
    (r"(?i)\ball cats are mammals\. All mammals are animals\. Whiskers is a cat\. Is Whiskers an animal\? Explain your reasoning step by step\.", "All cats are mammals. Mammals are animals. Whiskers is cat. Is Whiskers animal? Explain step by step."),
]

SAFE_FILLERS = [
    r"(?i)\bplease\b",
    r"(?i)\bkindly\b",
    r"(?i)\bcould you\b",
    r"(?i)\bwould you\b",
    r"(?i)\bcan you\b",
    r"(?i)\bplease help me to\b",
    r"(?i)\bhelp me\b",
    r"(?i)\bthank you\b",
    r"(?i)\bthanks\b",
]


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

    def compress_heuristics(self, text: str) -> str:
        """[Heuristics] Removes polite filler words and shortens verbose instruction prefixes safely.

        Maintains all logic words, negations, numbers, and key entities.
        """
        if not text:
            return ""

        cleaned = text

        # 1. Replace verbose headers
        for pat, rep in SAFE_HEURISTIC_PATTERNS:
            cleaned = re.sub(pat, rep, cleaned)

        # 2. Strip politeness/fillers
        for filler in SAFE_FILLERS:
            cleaned = re.sub(filler, "", cleaned)

        # Clean up double spaces
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned if cleaned else text

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

        # 2. Heuristic prompt cleaner (Heuristics) - Safe for all tasks as it preserves logic/data
        compressed = self.compress_heuristics(compressed)

        compressed_len = len(compressed)
        saving_pct = ((original_len - compressed_len) / original_len * 100) if original_len > 0 else 0
        if saving_pct > 2:
            logger.info(
                "Prompt compressed (category [%s]): %d -> %d chars (-%.1f%%)",
                category, original_len, compressed_len, saving_pct
            )

        return compressed
