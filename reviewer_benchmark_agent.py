import json
from ollama import chat


## System prompt for the Reviewer Agent (Benchmark)
SYSTEM_PROMPT = """
You are a benchmark reviewer agent for a mobile robot navigation system.
You will receive an IR-SIM benchmark report and a deterministic review.

The deterministic review already contains pass/fail verdicts computed
directly from the benchmark numbers. You must NOT change those booleans.
Your job is only to write clear text for the three text fields.

You must output ONLY a valid JSON object with EXACTLY these keys:
{
  "issue": "string",
  "likely_cause": "string",
  "recommendation": "string",
  "safety_passed": true or false,
  "goal_completion_passed": true or false,
  "efficiency_passed": true or false,
  "needs_revision": true or false
}

Rules:
- The four boolean fields MUST match the deterministic review exactly.
- "issue", "likely_cause", and "recommendation" must be strings.
- If a category passed, use "None" for the related explanation.
- Output ONLY the JSON. No markdown, no extra text.
"""


def validate_reviewer_benchmark_output(data):
    """Validate the Reviewer Agent's output for the benchmark report."""
    if not isinstance(data, dict):
        raise ValueError("Reviewer output is not a dict")

    required_keys = {
        "issue", "likely_cause", "recommendation",
        "safety_passed", "goal_completion_passed",
        "efficiency_passed", "needs_revision",
    }
    if set(data.keys()) != required_keys:
        raise ValueError(f"Reviewer output keys mismatch: {set(data.keys())}")

    for bool_key in ["safety_passed", "goal_completion_passed",
                     "efficiency_passed", "needs_revision"]:
        if not isinstance(data[bool_key], bool):
            raise ValueError(f"{bool_key} is not a boolean")

    for str_key in ["issue", "likely_cause", "recommendation"]:
        if not isinstance(data[str_key], str):
            raise ValueError(f"{str_key} is not a string")

    return True


def build_deterministic_review(benchmark_report):
    """Compute pass/fail booleans from the benchmark numbers."""
    results = benchmark_report.get("results", [])
    total_worlds = benchmark_report.get("total_worlds", 0)
    success_rate = benchmark_report.get("success_rate", 0.0)
    efficiency_rate = benchmark_report.get("efficiency_rate", 0.0)
    inefficient_success = benchmark_report.get("inefficient_success_worlds", 0)

    # Safety: any world where collision_or_done is True but goal not reached
    unsafe_worlds = [
        r for r in results
        if r.get("collision_or_done") and not r.get("reached_goal")
    ]
    safety_passed = len(unsafe_worlds) == 0

    # Goal completion: success rate must be 1.0 (all goals reached)
    goal_completion_passed = (success_rate >= 1.0 and total_worlds > 0)

    # Efficiency: no inefficient successes and efficiency rate is 1.0
    efficiency_passed = (inefficient_success == 0 and efficiency_rate >= 1.0)

    needs_revision = not (safety_passed and goal_completion_passed and efficiency_passed)

    # Compose deterministic issue text
    issues = []
    if not safety_passed:
        issues.append("Unsafe benchmark behavior detected")
    if not goal_completion_passed:
        issues.append("Goal completion failure")
    if not efficiency_passed:
        issues.append("Successful but inefficient navigation")

    issue_text = "; ".join(issues) if issues else "None"

    return {
        "issue": issue_text,
        "likely_cause": "None" if not issues else "See issue description",
        "recommendation": "None" if not issues else "Revise decide_next_move to address the issues above",
        "safety_passed": safety_passed,
        "goal_completion_passed": goal_completion_passed,
        "efficiency_passed": efficiency_passed,
        "needs_revision": needs_revision,
    }


def run_reviewer_benchmark(benchmark_report):
    """Run the Reviewer Agent on the benchmark report."""
    deterministic = build_deterministic_review(benchmark_report)

    last_error = None
    for attempt in range(1, 4):
        print(f"Benchmark Reviewer agent: attempt {attempt}/3 ...")

        user_content = json.dumps({
            "benchmark_report": benchmark_report,
            "deterministic_review": deterministic,
        })

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

        # Force booleans to match deterministic review
        for key in ["safety_passed", "goal_completion_passed",
                    "efficiency_passed", "needs_revision"]:
            parsed[key] = deterministic[key]

        try:
            validate_reviewer_benchmark_output(parsed)
        except ValueError as e:
            last_error = e
            print(f"  -> validation failed: {e}")
            continue

        return parsed

    # If LLM fails, fall back to deterministic review
    print("  -> falling back to deterministic review")
    return deterministic


## If run directly, load the benchmark report and review it.
if __name__ == "__main__":
    import os
    os.makedirs("artifacts", exist_ok=True)

    with open("artifacts/irsim_benchmark_report.json", "r", encoding="utf-8") as f:
        bench_report = json.load(f)

    review = run_reviewer_benchmark(bench_report)

    print("=== Benchmark Review Result ===")
    print(json.dumps(review, indent=2))

    with open("artifacts/benchmark_review.json", "w", encoding="utf-8") as f:
        json.dump(review, f, indent=2)

    print("\nSaved to artifacts/benchmark_review.json")