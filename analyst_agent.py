import json
from ollama import Client

REQUIRED_KEYS = {"goal", "allowed_actions", "safe_stop", "avoid_obstacles"}
PERMITTED_ACTIONS = {"FORWARD", "LEFT", "RIGHT", "STOP"}

SYSTEM_PROMPT = """
You are a requirements analyst agent for a mobile robot navigation system.
Read the customer brief and convert it into explicit software requirements.

Rules you must follow:
- The only permitted actions are: FORWARD, LEFT, RIGHT, STOP.
- Never invent any other action.
- "allowed_actions" must be a list containing only items from the permitted set.
- "safe_stop" must be a boolean.
- "avoid_obstacles" must be a boolean.
- "goal" must be a plain string.

Output ONLY valid JSON with exactly this structure, no markdown, no explanation:
{
  "goal": "string",
  "allowed_actions": ["FORWARD", "LEFT", "RIGHT", "STOP"],
  "safe_stop": true,
  "avoid_obstacles": true
}
"""

client = Client(host="http://127.0.0.1:11434", timeout=600)


def validate_requirements(result):
    if not isinstance(result, dict):
        return False

    present_keys = set(result.keys())
    if present_keys != REQUIRED_KEYS:
        return False

    if not isinstance(result["goal"], str):
        return False

    if not isinstance(result["allowed_actions"], list):
        return False

    for act in result["allowed_actions"]:
        if act not in PERMITTED_ACTIONS:
            return False

    if not isinstance(result["safe_stop"], bool):
        return False

    if not isinstance(result["avoid_obstacles"], bool):
        return False

    return True


def run_analyst(brief_text):
    # Retry a few times: smaller/larger local models occasionally wrap the JSON
    # in extra text; the validation gate catches that and we simply re-ask.
    last_error = None
    for attempt in range(1, 4):
        print(f"Analyst agent: attempt {attempt}/3 ...")

        response = client.chat(
            model="qwen3:8b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": brief_text},
            ],
            think=False,
            options={"num_predict": 1024},
        )

        raw_text = response.message.content.strip()
        
        
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.lower().startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        try:
            parsed_data = json.loads(raw_text)
        except json.JSONDecodeError as e:
            last_error = e
            print(f"  -> JSON parse failed: {e}")
            continue

        if not validate_requirements(parsed_data):
            last_error = ValueError("LLM output failed requirements validation check")
            print("  -> validation failed, retrying ...")
            continue

        return parsed_data

    raise ValueError(f"LLM output failed after retries. Last error: {last_error}")
