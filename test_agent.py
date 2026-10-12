import json
from ollama import chat


SYSTEM_PROMPT = """
You are a test agent for a mobile robot navigation system.
You will receive the requirements from the Analyst Agent and the plan from the Planner Agent.
Your job is to write pytest-style tests for the function decide_next_move(state).

The function signature is:
    def decide_next_move(state: dict) -> str

The 'state' dictionary has exactly these boolean keys:
    "goal_ahead", "goal_on_left", "goal_on_right",
    "front_blocked", "left_blocked", "right_blocked"

The function must return one of: "FORWARD", "LEFT", "RIGHT", "STOP".

Rules you must follow:
- Output ONLY Python code. No markdown, no explanations.
- The code must import pytest.
- The code must include: from generated.navigation_logic import decide_next_move
- Write one test function per scenario.
- Each test must assert the exact expected return value.
- Cover ALL of these scenarios:
  1. Goal ahead, not blocked      -> FORWARD
  2. Goal on left, not blocked    -> LEFT
  3. Goal on right, not blocked   -> RIGHT
  4. Front blocked, left free     -> LEFT
  5. Front blocked, right free    -> RIGHT
  6. All directions blocked       -> STOP
  7. Goal ahead but front blocked -> LEFT or RIGHT
  8. Goal on left but left blocked -> FORWARD or RIGHT
  9. Goal on right but right blocked -> FORWARD or LEFT
- Do NOT include any markdown fences.
"""


def validate_test_code(code_text):
    """Validate the generated test code."""
    if not isinstance(code_text, str) or not code_text.strip():
        return False

    # No markdown fences
    if "```" in code_text:
        return False

    required_keywords = [
        "import pytest",
        "from generated.navigation_logic import decide_next_move",
        "def test_",
        "assert",
    ]
    for kw in required_keywords:
        if kw not in code_text:
            return False

    try:
        compile(code_text, "<generated_test>", "exec")
    except SyntaxError:
        return False

    return True


def run_test_agent(requirements, plan):
    """Run the Test Agent, return validated test code."""
    last_error = None

    for attempt in range(1, 4):
        print(f"Test agent: attempt {attempt}/3 ...")
        print("  -> calling LLM (may take 1-3 minutes) ...")

        user_content = json.dumps({
            "requirements": requirements,
            "plan": plan,
        })

        response = chat(
            model="qwen3:8b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            think=False,
            options={"num_predict": 2048, "temperature": 0.2}
        )

        raw_text = response.message.content.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.lower().startswith("python"):
                raw_text = raw_text[6:]
            raw_text = raw_text.strip()

        if not validate_test_code(raw_text):
            last_error = ValueError("Generated test code failed validation")
            print("  -> validation failed, retrying ...")
            continue

        return raw_text

    raise ValueError(
        f"Test agent output failed after retries. Last error: {last_error}"
    )