
import json
from pathlib import Path

from developer_agent import run_developer


def main():
    with open("artifacts/plan.json", "r") as f:
        plan = json.load(f)

    code = run_developer(plan)

    with open("navigation_logic.py", "w") as f:
        f.write(code)

    print("Generated code saved to navigation_logic.py")


if __name__ == "__main__":
    main()
