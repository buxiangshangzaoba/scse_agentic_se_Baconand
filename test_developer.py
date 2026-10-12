import json
from pathlib import Path
from developer_agent import run_developer


def main():
    with open("artifacts/plan.json", "r") as f:
        plan = json.load(f)

    code = run_developer(plan)

    output_dir = Path("artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "navigation_logic.py", "w") as f:
        f.write(code)

    print("Generated code saved to artifacts/navigation_logic.py")
    print(code)


if __name__ == "__main__":
    main()