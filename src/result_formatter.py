"""
Result formatter module for HydraRoute Agent.
Formats and atomically writes results to /output/results.json.
"""

import json
import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger("hydraroute")


def format_results(results: list[dict]) -> list[dict]:
    """Format results to match the required output schema.

    Args:
        results: List of dicts with task_id and answer.

    Returns:
        Cleaned list matching schema: [{"task_id": "...", "answer": "..."}]
    """
    formatted = []
    for r in results:
        formatted.append({
            "task_id": str(r.get("task_id", "")),
            "answer": str(r.get("answer", "")),
        })
    return formatted


def save_results(results: list[dict], output_path: str) -> None:
    """Atomically write results to the output file.

    Writes to a temporary file first, then renames to the target path.
    This prevents partial/corrupt writes if the process is interrupted.

    Args:
        results: List of result dicts to write.
        output_path: Target file path (e.g. /output/results.json).
    """
    out_path = Path(output_path)

    # Ensure output directory exists
    out_path.parent.mkdir(parents=True, exist_ok=True)

    formatted = format_results(results)

    try:
        # Write to temp file in the same directory (so rename is atomic)
        fd, tmp_path = tempfile.mkstemp(
            dir=str(out_path.parent),
            suffix=".tmp",
            prefix="results_",
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(formatted, f, indent=2, ensure_ascii=False)
                f.write("\n")

            # Atomic rename
            os.replace(tmp_path, str(out_path))
            logger.info(
                "Results saved: %d tasks -> %s", len(formatted), output_path
            )
        except Exception:
            # Clean up temp file on error
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    except Exception as e:
        logger.error("Failed to save results atomically: %s", e)
        # Last-resort: write directly (non-atomic)
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(formatted, f, indent=2, ensure_ascii=False)
                f.write("\n")
            logger.info("Results saved (non-atomic fallback): %s", output_path)
        except Exception as e2:
            logger.critical("Cannot write results at all: %s", e2)
