from __future__ import annotations

import re
from dataclasses import dataclass

from .persistence import Persistence


@dataclass
class MemoryManager:
    persistence: Persistence

    def short_term(self) -> list[tuple[str, str]]:
        return self.persistence.get_recent_exchanges(3)

    def identity_facts(self) -> dict[str, str]:
        return self.persistence.get_identity_facts()

    def latest_summary(self) -> str:
        return self.persistence.get_latest_summary()

    def extract_identity_facts(self, user_message: str) -> dict[str, str]:
        text = user_message.strip()
        facts: dict[str, str] = {}

        patterns = {
            "name": r"\b(?:my name is|i am|i'm)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            "location": r"\b(?:i live in|i'm from|i am from)\s+([A-Za-z\s]+)",
            "job": r"\b(?:i work as|i am a|i'm a)\s+([A-Za-z\s]+)",
            "likes": r"\b(?:i like|i love)\s+([A-Za-z0-9\s,]+)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                facts[key] = re.sub(r"\s+", " ", match.group(1)).strip(" .,!?")

        if "favorite" in text.lower() and ":" in text:
            left, right = text.split(":", 1)
            if left.strip().lower().startswith("favorite"):
                facts[left.strip().lower().replace(" ", "_")] = right.strip()

        return facts

    def maybe_store_summary(self) -> str:
        count = self.persistence.get_exchange_count()
        if count == 0 or count % 10 != 0:
            return ""
        exchanges = self.persistence.get_last_n_exchanges(10)
        bullets = []
        for user, assistant in exchanges:
            u = user.strip().replace("\n", " ")[:120]
            a = assistant.strip().replace("\n", " ")[:120]
            bullets.append(f"- User: {u} | Assistant: {a}")
        summary = "Recent trajectory:\n" + "\n".join(bullets)
        self.persistence.add_summary(summary, turn_end=count)
        return summary
