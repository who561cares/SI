from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EmotionState:
    valence: float = 0.0
    arousal: float = 0.3
    intimacy: float = 0.0

    def update(self, user_message: str) -> None:
        text = user_message.lower()
        positive = sum(1 for token in ("thanks", "great", "love", "good", "awesome") if token in text)
        negative = sum(1 for token in ("bad", "hate", "angry", "upset", "annoyed") if token in text)
        personal = sum(1 for token in ("i am", "my", "me", "mine", "feel") if token in text)

        self.valence = self._clip(self.valence + 0.08 * (positive - negative))
        self.arousal = self._clip(self.arousal + 0.05 * (positive + negative) - 0.02)
        self.intimacy = self._clip(self.intimacy + 0.07 * personal)

    @staticmethod
    def _clip(value: float) -> float:
        return max(0.0, min(1.0, value))

    def sampling_controls(self, base_max_tokens: int) -> dict[str, float | int]:
        temperature = 0.4 + 0.8 * self.arousal
        top_p = 0.7 + 0.25 * self.valence
        max_tokens = int(base_max_tokens * (0.7 + 0.6 * self.intimacy))
        return {
            "temperature": round(max(0.1, min(1.4, temperature)), 3),
            "top_p": round(max(0.5, min(0.98, top_p)), 3),
            "max_tokens": max(32, min(220, max_tokens)),
        }
