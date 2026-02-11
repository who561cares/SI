from __future__ import annotations

from agent import AutonomousAgent


def main() -> None:
    agent = AutonomousAgent()
    print("Autonomous agent is running. Type 'exit' to quit.")
    try:
        while True:
            try:
                user_message = input("You: ").strip()
            except EOFError:
                break
            if not user_message:
                continue
            if user_message.lower() in {"exit", "quit"}:
                break
            reply = agent.reply(user_message)
            print(f"Agent: {reply}")
    except KeyboardInterrupt:
        print("\nInterrupted. Saving state and exiting...")
    finally:
        agent.close()


if __name__ == "__main__":
    main()
