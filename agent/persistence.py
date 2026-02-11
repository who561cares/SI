from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


class Persistence:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS exchanges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                assistant_reply TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS identity_memory (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS long_term_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary TEXT NOT NULL,
                turn_end INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def add_exchange(self, user_message: str, assistant_reply: str) -> None:
        self.conn.execute(
            "INSERT INTO exchanges(user_message, assistant_reply) VALUES (?, ?)",
            (user_message, assistant_reply),
        )
        self.conn.commit()

    def get_recent_exchanges(self, limit: int) -> list[tuple[str, str]]:
        cur = self.conn.execute(
            "SELECT user_message, assistant_reply FROM exchanges ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        return [(r["user_message"], r["assistant_reply"]) for r in reversed(rows)]

    def get_last_n_exchanges(self, n: int) -> list[tuple[str, str]]:
        return self.get_recent_exchanges(n)

    def get_exchange_count(self) -> int:
        cur = self.conn.execute("SELECT COUNT(*) AS c FROM exchanges")
        return int(cur.fetchone()["c"])

    def upsert_identity_facts(self, facts: dict[str, str]) -> None:
        for key, value in facts.items():
            self.conn.execute(
                """
                INSERT INTO identity_memory(key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, value),
            )
        self.conn.commit()

    def get_identity_facts(self) -> dict[str, str]:
        cur = self.conn.execute("SELECT key, value FROM identity_memory ORDER BY key ASC")
        return {row["key"]: row["value"] for row in cur.fetchall()}

    def add_summary(self, summary: str, turn_end: int) -> None:
        self.conn.execute(
            "INSERT INTO long_term_summaries(summary, turn_end) VALUES (?, ?)",
            (summary, turn_end),
        )
        self.conn.commit()

    def get_latest_summary(self) -> str:
        cur = self.conn.execute(
            "SELECT summary FROM long_term_summaries ORDER BY id DESC LIMIT 1"
        )
        row = cur.fetchone()
        return row["summary"] if row else ""

    def set_state(self, key: str, value: str) -> None:
        self.conn.execute(
            """
            INSERT INTO state(key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
            """,
            (key, value),
        )
        self.conn.commit()

    def get_state(self, key: str, default: str = "") -> str:
        cur = self.conn.execute("SELECT value FROM state WHERE key = ?", (key,))
        row = cur.fetchone()
        return row["value"] if row else default

    def close(self) -> None:
        self.conn.close()
