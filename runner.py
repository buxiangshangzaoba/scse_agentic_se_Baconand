import json
import os

from generated.navigation_logic import decide_next_move


## Define a set of scenarios to test the navigation logic.
## Each scenario has a state (input) and an expected output.
SCENARIOS = [
    # Goal ahead, front free -> FORWARD
    {
        "name": "goal_ahead_clear",
        "state": {
            "goal_ahead": True, "goal_on_left": False, "goal_on_right": False,
            "front_blocked": False, "left_blocked": False, "right_blocked": False,
        },
        "expected": "FORWARD",
    },
    # Goal on left, left free -> LEFT
    {
        "name": "goal_left_clear",
        "state": {
            "goal_ahead": False, "goal_on_left": True, "goal_on_right": False,
            "front_blocked": False, "left_blocked": False, "right_blocked": False,
        },
        "expected": "LEFT",
    },
    # Goal on right, right free -> RIGHT
    {
        "name": "goal_right_clear",
        "state": {
            "goal_ahead": False, "goal_on_left": False, "goal_on_right": True,
            "front_blocked": False, "left_blocked": False, "right_blocked": False,
        },
        "expected": "RIGHT",
    },
    # Front blocked, left free -> LEFT
    {
        "name": "front_blocked_left_free",
        "state": {
            "goal_ahead": True, "goal_on_left": False, "goal_on_right": False,
            "front_blocked": True, "left_blocked": False, "right_blocked": True,
        },
        "expected": "LEFT",
    },
    # Front blocked, right free -> RIGHT
    {
        "name": "front_blocked_right_free",
        "state": {
            "goal_ahead": True, "goal_on_left": False, "goal_on_right": False,
            "front_blocked": True, "left_blocked": True, "right_blocked": False,
        },
        "expected": "RIGHT",
    },
    # All blocked -> STOP
    {
        "name": "all_blocked",
        "state": {
            "goal_ahead": False, "goal_on_left": False, "goal_on_right": False,
            "front_blocked": True, "left_blocked": True, "right_blocked": True,
        },
        "expected": "STOP",
    },
    # Goal ahead, front free, both sides free -> FORWARD
    {
        "name": "goal_ahead_all_free",
        "state": {
            "goal_ahead": True, "goal_on_left": True, "goal_on_right": False,
            "front_blocked": False, "left_blocked": False, "right_blocked": False,
        },
        "expected": "FORWARD",
    },
]


def run_simulation():
    """Run all scenarios and return a summary report."""
    results = []
    passed = 0
    failed = 0

    for scenario in SCENARIOS:
        state = scenario["state"]
        expected = scenario["expected"]

        try:
            actual = decide_next_move(state)
        except Exception as e:
            actual = f"ERROR: {e}"

        ok = (actual == expected)
        if ok:
            passed += 1
        else:
            failed += 1

        results.append({
            "name": scenario["name"],
            "state": state,
            "expected": expected,
            "actual": actual,
            "passed": ok,
        })

    total = len(SCENARIOS)
    success_rate = passed / total if total > 0 else 0.0

    report = {
        "total_scenarios": total,
        "passed": passed,
        "failed": failed,
        "success_rate": success_rate,
        "results": results,
    }
    return report


if __name__ == "__main__":
    os.makedirs("artifacts", exist_ok=True)

    report = run_simulation()

    print("=== Simulation Report ===")
    print(f"Total: {report['total_scenarios']}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
    print(f"Success rate: {report['success_rate']:.2%}")

    print("\nDetailed results:")
    for r in report["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] {r['name']}: expected={r['expected']}, actual={r['actual']}")

    with open("artifacts/simulation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\nSaved to artifacts/simulation_report.json")