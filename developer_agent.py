## The logic is fairly similar to the Analyst and Planner agents
import json
from ollama import chat

## System prompt for the Developer Agent
SYSTEM_PROMPT = """
You are a developer agent for a mobile robot navigation system.
You will receive a navigation plan from the Planner Agent.
Your job is to write Python code that implements this plan.

Rules:
- The output must be valid Python code only. No markdown, no explanations.
- The code must contain a function called decide_next_move(state).
- The function must return one of: "FORWARD", "LEFT", "RIGHT", "STOP".
- The input 'state' is a dictionary with boolean keys: "goal_ahead", "goal_on_left", "goal_on_right", "front_blocked", "left_blocked", "right_blocked".
- The code must handle blocked directions and goal direction.
- The code must never move into a blocked direction.
- If no safe direction is available, the robot must stop.

Output ONLY Python code.
"""

def validate_code(code_text):
    if not isinstance(code_text, str):
        return False

    if "def decide_next_move" not in code_text:
        return False

    try:
        compile(code_text, "<generated>", "exec")
    except SyntaxError:
        return False

    return True

## Function to run the Developer Agent
def run_developer(plan):
    last_error = None
    for attempt in range(1, 4):
        print(f"Developer agent: attempt {attempt}/3 ...")

        response = chat(
            model="qwen3:8b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(plan)}
            ]
        )

        raw_text = response.message.content.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.lower().startswith("python"):
                raw_text = raw_text[6:]
            raw_text = raw_text.strip()

        if not validate_code(raw_text):
            last_error = ValueError("Generated code failed validation")
            print("  -> validation failed, retrying ...")
            continue

        return raw_text

    raise ValueError(f"Developer output failed after retries. Last error: {last_error}")


REVISION_SYSTEM_PROMPT = """
You are a developer agent for a mobile robot navigation system.
You have already produced an initial version of decide_next_move(state).
Now you have received:
- The original navigation code
- Review notes from the Reviewer Agent
- A benchmark report from IR-SIM
- The requirements
- The navigation plan

Your job is to write an IMPROVED version of decide_next_move(state)
that addresses the issues found in the review and benchmark.

Rules:
- Output ONLY valid Python code. No markdown, no explanations.
- The code must contain a function called decide_next_move(state).
- The function must return one of: "FORWARD", "LEFT", "RIGHT", "STOP".
- The input 'state' is a dictionary with boolean keys:
    "goal_ahead", "goal_on_left", "goal_on_right",
    "front_blocked", "left_blocked", "right_blocked".
- The code must never move into a blocked direction.
- If no safe direction is available, the robot must stop.
- Keep the interface identical to the original code.

Output ONLY Python code.
"""


def run_developer_revision(original_code, review_notes, benchmark_report, requirements, plan):
    """
    Run the Developer Agent in revision mode.
    Returns a new version of decide_next_move as a string.
    """
    last_error = None

    for attempt in range(1, 4):
        print(f"Developer revision: attempt {attempt}/3 ...")

        user_content = json.dumps({
            "original_code": original_code,
            "review_notes": review_notes,
            "benchmark_report": benchmark_report,
            "requirements": requirements,
            "plan": plan,
        })

        response = chat(
            model="qwen3:8b",
            messages=[
                {"role": "system", "content": REVISION_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            think=False,
            options={"num_predict": 2048, "temperature": 0.2},
        )

        raw_text = response.message.content.strip()

        # Strip markdown fences if present
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.lower().startswith("python"):
                raw_text = raw_text[6:]
            raw_text = raw_text.strip()

        if not validate_code(raw_text):
            last_error = ValueError("Revised code failed validation")
            print("  -> validation failed, retrying ...")
            continue

        return raw_text

    raise ValueError(
        f"Developer revision failed after retries. Last error: {last_error}"
    )