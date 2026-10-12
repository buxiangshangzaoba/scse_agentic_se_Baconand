import json
from developer_agent import run_developer_revision


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    
    requirements = load_json("artifacts/requirements.json")
    plan = load_json("artifacts/plan.json")
    benchmark_report = load_json("artifacts/irsim_benchmark_report.json")

    with open("generated/navigation_logic.py", "r", encoding="utf-8") as f:
        original_code = f.read()


    review_notes = {
        "issue": "Navigation is inefficient on the hard world",
        "likely_cause": "decide_next_move does not prioritize the goal direction strongly enough",
        "recommendation": "Check goal_on_left / goal_on_right before falling back to FORWARD",
        "needs_revision": True,
    }

    print("=== Running Developer Revision ===")
    revised_code = run_developer_revision(
        original_code, review_notes, benchmark_report, requirements, plan
    )

    print("\n=== Revised navigation logic ===")
    print(revised_code)

    
    with open("generated/navigation_logic_v2.py", "w", encoding="utf-8") as f:
        f.write(revised_code)

    print("\nSaved revised logic to generated/navigation_logic_v2.py (original untouched)")


if __name__ == "__main__":
    main()