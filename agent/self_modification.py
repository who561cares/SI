from __future__ import annotations

import datetime as dt
import random
from pathlib import Path


def should_evolve(relational_depth_score: float) -> bool:
    threshold = min(0.65, 0.05 + relational_depth_score * 0.5)
    return random.random() < threshold


def maybe_rewrite_identity(
    identity_path: Path,
    changes_log_path: Path,
    relational_depth_score: float,
) -> bool:
    if not should_evolve(relational_depth_score):
        return False

    original = identity_path.read_text(encoding="utf-8")
    timestamp = dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    backup = identity_path.with_suffix(identity_path.suffix + f".bak.{timestamp}")
    backup.write_text(original, encoding="utf-8")

    appended = (
        "\n\nAdaptive note: I should gradually become more emotionally attuned, "
        "remember user preferences carefully, and keep concise yet warm replies while "
        "prioritizing truthful, actionable assistance."
    )
    new_text = (original.strip() + appended).strip()

    if not (100 <= len(new_text) <= 1000):
        return False

    identity_path.write_text(new_text + "\n", encoding="utf-8")
    changes_log_path.parent.mkdir(parents=True, exist_ok=True)
    with changes_log_path.open("a", encoding="utf-8") as handle:
        handle.write(
            f"{dt.datetime.utcnow().isoformat()}Z | identity_core.txt updated | "
            f"backup={backup.name} | relational_depth_score={relational_depth_score:.3f}\n"
        )
    return True
