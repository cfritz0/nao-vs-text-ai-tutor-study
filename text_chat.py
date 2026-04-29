import os
from datetime import datetime
from openai import OpenAI

CHAT_MODEL = "gpt-4.1-mini"
SYSTEM_PROMPT = "You are a college tutor in Computer Science. Keep answers concise and conversational."
MAX_TURNS = 5

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

# Keep a full transcript separate from the trimmed chat history
conversation_log = []


# ANSI terminal colors
RESET = "\033[0m"
TUTOR_COLOR = "\033[96m"   # bright cyan
STUDENT_COLOR = "\033[93m" # bright yellow


def ask_llm(user_text):
    # Log full user message
    conversation_log.append({"role": "user", "content": user_text})

    # Add user message to active model history
    history.append({"role": "user", "content": user_text})

    resp = client.responses.create(
        model=CHAT_MODEL,
        input=history,
    )

    reply = (resp.output_text or "").strip()

    # Log and store assistant reply
    conversation_log.append({"role": "assistant", "content": reply})
    history.append({"role": "assistant", "content": reply})

    # Trim model history, but keep system prompt
    if len(history) > 1 + (2 * MAX_TURNS):
        history[:] = [history[0]] + history[-(2 * MAX_TURNS):]

    return reply


def save_conversation_log():
    if not conversation_log:
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_log_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write("Text Chat Conversation Log\n")
        f.write(f"Saved: {datetime.now().isoformat()}\n")
        f.write("=" * 50 + "\n\n")

        for entry in conversation_log:
            if entry["role"] == "user":
                speaker = "Student"
            elif entry["role"] == "assistant":
                speaker = "Text tutor"
            else:
                speaker = entry["role"]

            f.write(f"{speaker}: {entry['content']}\n\n")

    return filename


def main():
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set.")

    print("Text → LLM chat (type 'quit' to exit)\n")

    log_file = None

    try:
        while True:
            try:
                user_input = input(f"{STUDENT_COLOR}Student:{RESET} ").strip()
            except KeyboardInterrupt:
                print("")
                break

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit"]:
                break

            reply = ask_llm(user_input)

            print(f"{TUTOR_COLOR}Text Tutor:{RESET} {reply}")
            print("")

    finally:
        log_file = save_conversation_log()
        if log_file:
            print(f"Conversation saved to: {log_file}")

    print("Goodbye.")


if __name__ == "__main__":
    main()
