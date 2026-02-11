from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GoalState:
    helpfulness: float = 0.5
    curiosity: float = 0.5
    relational_depth_score: float = 0.2

    def update(self, user_message: str) -> None:
        text = user_message.lower()
        asks_help = "?" in text or any(w in text for w in ("help", "how", "can you"))
        personal = any(w in text for w in ("i ", "my ", "feel", "family", "work"))

        self.helpfulness = self._clip(self.helpfulness + (0.06 if asks_help else -0.01))
        self.curiosity = self._clip(self.curiosity + (0.03 if len(text.split()) > 6 else -0.01))
        self.relational_depth_score = self._clip(
            self.relational_depth_score + (0.07 if personal else 0.01)
        )

    @staticmethod
    def _clip(value: float) -> float:
        return max(0.0, min(1.0, value))
