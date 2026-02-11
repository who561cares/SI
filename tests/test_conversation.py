from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import AgentConfig
from agent.conversation import AutonomousAgent


def test_conversation_reply_and_identity_memory(tmp_path: Path) -> None:
    identity_file = tmp_path / "identity_core.txt"
    identity_file.write_text(
        "You are a concise, warm assistant focused on useful and honest conversation.",
        encoding="utf-8",
    )
    changes_log = tmp_path / "changes.log"
    config = AgentConfig(
        sqlite_path=str(tmp_path / "agent_state.db"),
        identity_path=str(identity_file),
        changes_log_path=str(changes_log),
    )

    agent = AutonomousAgent(config)
    try:
        reply = agent.reply("Hi, my name is Alice and I live in Nairobi.")
        assert isinstance(reply, str)
        assert reply.strip() != ""

        facts = agent.persistence.get_identity_facts()
        assert facts.get("name", "").lower().startswith("alice")
        assert "nairobi" in facts.get("location", "").lower()
    finally:
        agent.close()
