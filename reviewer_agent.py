import json
from ollama import chat


SYSTEM_PROMPT = """
You are a reviewer agent for a mobile robot navigation system.
You will receive a simulation report from the Simulation Runner.
The report contains the results of testing the decide_next_move function
across multiple scenarios.

Your job is to analyze the report and identify any problems.

You must output ONLY a valid JSON object with EXACTLY these keys:
{
  "issue": "string describing the main problem, or 'None' if everything passed",
  "likely_cause": "string describing the likely cause, or 'None' if no problem",
  "recommendation": "string with improvement suggestion, or 'None' if no problem",
  "needs_revision": true or false
}

Rules:
- "needs_revision" must be a boolean (true or false).
- The other three keys must be strings.
- If all scenarios passed (failed == 0), set "needs_revision" to false
  and use "None" for the other fields.
- If any scenario failed, set "needs_revision" to true and fill in the fields.
- Output ONLY the JSON. No markdown, no explanation, no extra text.
"""


def validate_reviewer_output(data):
    """Validate the Reviewer Agent's output."""
    if not isinstance(data, dict):
        return False

    required_keys = {"issue", "likely_cause", "recommendation", "needs_revision"}
    if set(data.keys()) != required_keys:
        return False

    if not isinstance(data["needs_revision"], bool):
        return False

    for key in ["issue", "likely_cause", "recommendation"]:
        if not isinstance(data[key], str):
            return False

    return True


def run_reviewer(simulation_report):
    """Run the Reviewer Agent on the simulation report."""
    last_error = None

    for attempt in range(1, 4):
        print(f"Reviewer agent: attempt {attempt}/3 ...")

        user_content = json.dumps(simulation_report)

        response = chat(
            model="qwen3:8b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            think=False,
            options={"num_predict": 1024, "temperature": 0.2}
        )

        raw_text = response.message.content.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.lower().startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as e:
            last_error = e
            print(f"  -> JSON parse failed: {e}")
            continue

        if not validate_reviewer_output(parsed):
            last_error = ValueError("Reviewer output failed schema validation")
            print("  -> validation failed, retrying ...")
            continue

        return parsed

    raise ValueError(f"Reviewer output failed after retries. Last error: {last_error}")


if __name__ == "__main__":
    import os
    os.makedirs("artifacts", exist_ok=True)

    with open("artifacts/simulation_report.json", "r", encoding="utf-8") as f:
        sim_report = json.load(f)

    review = run_reviewer(sim_report)

    print("=== Review Result ===")
    print(json.dumps(review, indent=2))

    with open("artifacts/review_result.json", "w", encoding="utf-8") as f:
        json.dump(review, f, indent=2)

    print("\nSaved to artifacts/review_result.json")