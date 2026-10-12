import json
from pathlib import Path


## Create a function/logic that reads the requirements from requirements.json, 
# then calls the run_planner function with the requirements as input, and finally writes the validated plan to plan.json. 
from planner_agent import run_planner


def main():
    with open("artifacts/requirements.json", "r") as f:
        requirements = json.load(f)

    plan = run_planner(requirements)

    output_dir = Path("artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "plan.json", "w") as f:
        json.dump(plan, f, indent=2)

    print("Validated plan saved to artifacts/plan.json")
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()