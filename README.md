# Autonomous Conversational Agent (Python + llama.cpp)

A production-style autonomous conversational agent built in Python, with:

- Local inference via `llama-cpp-python`
- Persistent SQLite memory across sessions
- Emotion-influenced generation controls
- Probabilistic reflection and self-evolution
- Constrained self-modification (identity text only)

This repository targets **Python 3.11+** and **Termux (Android)**.

---

## Project Structure

```text
run_agent.py
config.py
logs/changes.log

agent/
    __init__.py
    conversation.py
    prompt_builder.py
    memory.py
    persistence.py
    emotion.py
    goals.py
    reflection.py
    self_modification.py
    identity_core.txt

tests/
    test_conversation.py
```

---

## Core Features

### 1) LLM Integration (`llama_cpp.Llama`)

- Uses `llama_cpp.Llama` as the backend model runner.
- Default context window: `n_ctx = 768`
- Default generation length: `max_tokens = 80`
- `n_threads` configurable through environment variable.
- `_llama_generate()`:
  - Calls the model
  - Removes `User:` and `Assistant:` tags from output
  - Strips whitespace
  - Returns minimal fallback text if generation fails

### 2) Emotional Engine

Tracks three dimensions each turn:

- `valence`
- `arousal`
- `intimacy`

These influence sampling controls:

- `arousal -> temperature`
- `valence -> top_p`
- `intimacy -> max_tokens`

### 3) Multi-Layer Memory (SQLite)

Memory persists in SQLite and survives restarts.

- **Short-term memory**: last 3 exchanges only
- **Identity memory**: key-value user facts extracted from user messages
- **Long-term summary memory**: summarizes every 10 turns, stores compressed summary, and injects only the summary (not full raw older history)

### 4) Prompt Construction

Each prompt includes:

1. `identity_core.txt`
2. Known user facts
3. Latest long-term summary (if available)
4. Short-term memory exchanges
5. Current user message

Prompt excludes internal telemetry/scoring numbers.

### 5) Hybrid Self-Modification (Guarded)

Self-modification logic is intentionally constrained:

- Only modifies `agent/identity_core.txt`
- Creates timestamped backup before rewrite
- Logs change in `logs/changes.log`
- Never modifies `.py` files
- Never deletes files
- Validates rewritten identity size is between 100 and 1000 chars
- Aborts rewrite if validation fails

Evolution trigger is probabilistic and uses `random.random()`, scaled by `relational_depth_score`.

### 6) Behavioral Autonomy

No deterministic turn-index triggers are used for reflection/evolution. Both are probability-based.

### 7) Runtime Loop

`run_agent.py` performs the full autonomous loop:

- Loads persistent state/memory from SQLite
- Reads user input from stdin
- Updates emotion + goals per turn
- Generates reply
- Persists exchanges and state
- Optionally reflects and self-modifies
- Handles `Ctrl+C` cleanly

### 8) Safety Boundaries

The code avoids:

- `eval`
- dynamic `exec`
- shell calls from Python runtime logic
- unrestricted filesystem traversal

Self-modification is strictly limited to `identity_core.txt`.

---

## Requirements

- Python 3.11+ (project code)
- `llama-cpp-python`
- Local model file (default):

```text
/data/data/com.termux/files/home/models/Wizard-Vicuna-7B-Uncensored.Q4_K_M.gguf
```

Install dependencies (minimal):

```bash
pip install llama-cpp-python pytest
```

---

## Configuration

Environment variables:

- `AGENT_MODEL_PATH` (default shown above)
- `AGENT_N_CTX` (default: `768`)
- `AGENT_MAX_TOKENS` (default: `80`)
- `AGENT_N_THREADS` (default: CPU count)
- `AGENT_DB_PATH` (default: `agent_state.db`)

Example:

```bash
export AGENT_MODEL_PATH="/data/data/com.termux/files/home/models/Wizard-Vicuna-7B-Uncensored.Q4_K_M.gguf"
export AGENT_N_THREADS=4
```

---

## Running the Agent

```bash
python run_agent.py
```

Usage:

- Type messages at `You:` prompt
- Type `exit` or `quit` to stop
- Press `Ctrl+C` for graceful interruption

---

## Running Tests

```bash
pytest -q
```

The test suite currently validates:

- Agent instantiation
- Non-empty reply generation
- Identity memory extraction + persistence update

---

## Persistence Overview

SQLite tables created automatically:

- `exchanges`
- `identity_memory`
- `long_term_summaries`
- `state`

This design allows conversation continuity between sessions.

---

## Notes for Termux

- Keep model path on device storage with sufficient free RAM/storage.
- Tune `AGENT_N_THREADS` based on your device CPU for latency/thermals.
- Smaller quantized GGUF models are recommended for smoother mobile usage.

---

## License

No explicit license file is included in this repo snapshot. Add one if needed for distribution.
