from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PromptBuilder:
    identity_file: Path

    def identity_core(self) -> str:
        return self.identity_file.read_text(encoding="utf-8").strip()

    def build(
        self,
        user_message: str,
        short_term: list[tuple[str, str]],
        identity_facts: dict[str, str],
        long_term_summary: str,
    ) -> str:
        identity_block = self.identity_core()
        facts_block = "\n".join(f"- {k}: {v}" for k, v in identity_facts.items())
        if not facts_block:
            facts_block = "- No stable facts yet."

        stm_lines: list[str] = []
        for user, assistant in short_term:
            stm_lines.append(f"User: {user}")
            stm_lines.append(f"Assistant: {assistant}")
        if not stm_lines:
            stm_lines.append("No recent exchange history.")
        short_term_block = "\n".join(stm_lines)

        summary_block = long_term_summary.strip() if long_term_summary else "No long-term summary yet."

        return (
            f"{identity_block}\n\n"
            "Known about user:\n"
            f"{facts_block}\n\n"
            "Long-term summary:\n"
            f"{summary_block}\n\n"
            "Short-term memory:\n"
            f"{short_term_block}\n\n"
            "Respond helpfully and naturally.\n"
            f"User: {user_message}\n"
            "Assistant:"
        )
