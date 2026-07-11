"""
Task loader module for HydraRoute Agent.
Loads and validates tasks from /input/tasks.json.
"""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger("hydraroute")

REQUIRED_FIELDS = {"task_id", "category", "instruction"}


def load_tasks(input_path: str) -> list[dict]:
    """Load and validate tasks from JSON file.

    Args:
        input_path: Path to the tasks JSON file.

    Returns:
        List of validated task dicts with keys: task_id, category, instruction.

    Raises:
        SystemExit: If the file cannot be loaded (produces empty output instead).
    """
    path = Path(input_path)

    if not path.exists():
        logger.error("Tasks file not found: %s", input_path)
        return []

    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in tasks file: %s", e)
        return []
    except OSError as e:
        logger.error("Failed to read tasks file: %s", e)
        return []

    if not isinstance(data, list):
        logger.error("Tasks file must contain a JSON array, got %s", type(data).__name__)
        return []

    tasks: list[dict] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            logger.warning("Skipping task at index %d: not a dict", i)
            continue

        missing = REQUIRED_FIELDS - set(item.keys())
        if missing:
            logger.warning(
                "Skipping task at index %d: missing fields %s", i, missing
            )
            continue

        tasks.append({
            "task_id": str(item["task_id"]),
            "category": str(item["category"]).strip().lower(),
            "instruction": str(item["instruction"]),
        })

    logger.info("Loaded %d valid tasks from %s", len(tasks), input_path)
    return tasks


def ensure_output_dir(output_path: str) -> None:
    """Create output directory if it doesn't exist."""
    out_dir = Path(output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    logger.debug("Output directory ensured: %s", out_dir)
