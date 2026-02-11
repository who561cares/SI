from __future__ import annotations

import json
from dataclasses import asdict

from config import AgentConfig
from .emotion import EmotionState
from .goals import GoalState
from .memory import MemoryManager
from .persistence import Persistence
from .prompt_builder import PromptBuilder
from .reflection import should_reflect
from .self_modification import maybe_rewrite_identity


class AutonomousAgent:
    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()
        self.persistence = Persistence(self.config.sqlite_path)
        self.memory = MemoryManager(self.persistence)
        self.prompt_builder = PromptBuilder(self.config.identity_file)
        self.emotion = self._load_emotion()
        self.goals = self._load_goals()
        self.llm = self._load_llm()

    def _load_llm(self):
        try:
            from llama_cpp import Llama

            return Llama(
                model_path=self.config.model_path,
                n_ctx=self.config.n_ctx,
                n_threads=self.config.n_threads,
                verbose=False,
            )
        except Exception:
            return None

    def _load_emotion(self) -> EmotionState:
        raw = self.persistence.get_state("emotion", "")
        if not raw:
            return EmotionState()
        data = json.loads(raw)
        return EmotionState(**data)

    def _load_goals(self) -> GoalState:
        raw = self.persistence.get_state("goals", "")
        if not raw:
            return GoalState()
        data = json.loads(raw)
        return GoalState(**data)

    def _save_state(self) -> None:
        self.persistence.set_state("emotion", json.dumps(asdict(self.emotion)))
        self.persistence.set_state("goals", json.dumps(asdict(self.goals)))

    def _llama_generate(self, prompt: str, controls: dict[str, float | int]) -> str:
        try:
            if self.llm is None:
                raise RuntimeError("LLM unavailable")
            output = self.llm(
                prompt,
                max_tokens=int(controls["max_tokens"]),
                temperature=float(controls["temperature"]),
                top_p=float(controls["top_p"]),
                stop=["\nUser:"],
            )
            text = output["choices"][0]["text"]
            clean = text.replace("User:", "").replace("Assistant:", "").strip()
            return clean or "I hear you. Could you share a little more detail so I can help better?"
        except Exception:
            return "I’m here with you. I had a brief generation issue, but I can still help—please continue."

    def reply(self, user_message: str) -> str:
        self.emotion.update(user_message)
        self.goals.update(user_message)

        facts = self.memory.extract_identity_facts(user_message)
        if facts:
            self.persistence.upsert_identity_facts(facts)

        prompt = self.prompt_builder.build(
            user_message=user_message,
            short_term=self.memory.short_term(),
            identity_facts=self.memory.identity_facts(),
            long_term_summary=self.memory.latest_summary(),
        )
        controls = self.emotion.sampling_controls(self.config.max_tokens)
        assistant_reply = self._llama_generate(prompt, controls)

        self.persistence.add_exchange(user_message, assistant_reply)
        self.memory.maybe_store_summary()

        if should_reflect(self.goals):
            reflection_note = (
                "reflection: stay grounded in user goals, remember stable preferences, "
                "and keep responses concise and practical"
            )
            self.persistence.set_state("reflection", reflection_note)

        maybe_rewrite_identity(
            identity_path=self.config.identity_file,
            changes_log_path=self.config.changes_log_file,
            relational_depth_score=self.goals.relational_depth_score,
        )
        self._save_state()
        return assistant_reply

    def close(self) -> None:
        self.persistence.close()
