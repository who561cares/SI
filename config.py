from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AgentConfig:
    model_path: str = os.getenv(
        "AGENT_MODEL_PATH",
        "/data/data/com.termux/files/home/models/Wizard-Vicuna-7B-Uncensored.Q4_K_M.gguf",
    )
    n_ctx: int = int(os.getenv("AGENT_N_CTX", "768"))
    max_tokens: int = int(os.getenv("AGENT_MAX_TOKENS", "80"))
    n_threads: int = int(os.getenv("AGENT_N_THREADS", str(os.cpu_count() or 2)))
    sqlite_path: str = os.getenv("AGENT_DB_PATH", "agent_state.db")
    identity_path: str = "agent/identity_core.txt"
    changes_log_path: str = "logs/changes.log"

    @property
    def sqlite_file(self) -> Path:
        return Path(self.sqlite_path)

    @property
    def identity_file(self) -> Path:
        return Path(self.identity_path)

    @property
    def changes_log_file(self) -> Path:
        return Path(self.changes_log_path)
