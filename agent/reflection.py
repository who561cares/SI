from __future__ import annotations

import random

from .goals import GoalState


def should_reflect(goals: GoalState) -> bool:
    base = 0.08
    probability = min(0.55, base + goals.curiosity * 0.25 + goals.relational_depth_score * 0.2)
    return random.random() < probability
