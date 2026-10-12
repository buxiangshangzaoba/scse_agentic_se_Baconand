from ollama import Client

client = Client(host="http://127.0.0.1:11434", timeout=600)


def main():

    with open("brief.txt", "r", encoding="utf-8") as f:
        brief_text = f.read()

    system_prompt = """
    You are a requirements engineer.
    Read the given customer brief, produce human-readable natural-language software requirements for the robot.
    Write clear numbered plain-text requirements.
    List allowed robot actions at the end.
    Do NOT output JSON, do NOT use markdown code blocks. Output only plain English text.
    """

    print("Asking qwen3:8b ... (first model load may take 1-3 minutes, please wait)")

    # stream=True: print tokens as they are generated, so the script never looks frozen.
    # think=False: disable Qwen3's internal reasoning trace and answer directly.
    collected = []
    for chunk in client.chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": brief_text},
        ],
        think=False,
        stream=True,
        options={"num_predict": 512},
    ):
        piece = chunk["message"]["content"]
        print(piece, end="", flush=True)
        collected.append(piece)

    llm_generated_text = "".join(collected).strip()

    with open("robot_requirements.txt", "w", encoding="utf-8") as outfile:
        outfile.write(llm_generated_text)

    print("\n\nOutput saved to robot_requirements.txt")


if __name__ == "__main__":
    main()
