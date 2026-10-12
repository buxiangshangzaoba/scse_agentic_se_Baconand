from pathlib import Path
import json
from analyst_agent import run_analyst


def main():
    with open("brief.txt", "r") as f:
        brief_content = f.read()

    requirements = run_analyst(brief_content)

    output_dir = Path("artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "requirements.json"

    with open(output_path, "w") as outfile:
        json.dump(requirements, outfile, indent=2)

    print(f"Validated requirements saved to {output_path}")
    print(json.dumps(requirements, indent=2))


if __name__ == "__main__":
    main()
