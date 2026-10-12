import json
import subprocess
import ast
import os
import sys


WORLD_FILES = [
    "irsim_worlds/world_easy.yaml",
    "irsim_worlds/world_medium.yaml",
    "irsim_worlds/world_hard.yaml",
    "irsim_worlds/world_custom.yaml",
]

ARTIFACTS_DIR = "artifacts"


def run_benchmark_for_world(world_file):
    """
    Run test_irsim_with_agent.py for a given world file,
    capture its stdout, and extract the IR-SIM report dict.
    """
    print(f"\n=== Benchmarking: {world_file} ===")
    try:
        result = subprocess.run(
            [sys.executable, "test_irsim_with_agent.py", world_file],
            capture_output=True,
            text=True,
            timeout=900,
        )
    except subprocess.TimeoutExpired:
        print(f"  -> TIMEOUT on {world_file}")
        return None

    output = result.stdout
    print("--- subprocess stdout (tail) ---")
    print("\n".join(output.splitlines()[-20:]))

    if result.returncode != 0:
        print(f"  -> subprocess failed with code {result.returncode}")
        print("--- stderr ---")
        print(result.stderr[-1000:])
        return None

    marker = "IR-SIM report:"
    idx = output.find(marker)
    if idx == -1:
        print("  -> could not find 'IR-SIM report:' marker in output")
        return None

    tail = output[idx + len(marker):].strip()
    start = tail.find("{")
    if start == -1:
        return None

    depth = 0
    end = -1
    for i in range(start, len(tail)):
        if tail[i] == "{":
            depth += 1
        elif tail[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    if end == -1:
        return None

    dict_str = tail[start:end]
    try:
        report = ast.literal_eval(dict_str)
    except (ValueError, SyntaxError) as e:
        print(f"  -> failed to parse report: {e}")
        return None

    return report


def main():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    results = []
    reached_goal_count = 0
    efficient_count = 0
    inefficient_success_count = 0
    failed_count = 0
    total_steps = 0

    for world_file in WORLD_FILES:
        report = run_benchmark_for_world(world_file)

        if report is None:
            results.append({
                "world": world_file,
                "reached_goal": False,
                "collision_or_done": False,
                "steps_taken": 0,
                "efficiency_status": "failed",
                "error": "no report",
            })
            failed_count += 1
            continue

        report["world"] = world_file
        results.append(report)

        reached = report.get("reached_goal", False)
        steps = report.get("steps_taken", 0)
        status = report.get("efficiency_status", "failed")

        total_steps += steps

        if reached:
            reached_goal_count += 1
            if status == "efficient":
                efficient_count += 1
            else:
                inefficient_success_count += 1
        else:
            failed_count += 1

    total = len(WORLD_FILES)
    success_rate = reached_goal_count / total if total > 0 else 0.0
    efficiency_rate = efficient_count / total if total > 0 else 0.0
    average_steps = total_steps / total if total > 0 else 0.0

    benchmark_report = {
        "total_worlds": total,
        "goals_reached": reached_goal_count,
        "success_rate": success_rate,
        "efficient_worlds": efficient_count,
        "inefficient_success_worlds": inefficient_success_count,
        "failed_worlds": failed_count,
        "efficiency_rate": efficiency_rate,
        "average_steps_taken": average_steps,
        "results": results,
    }

    out_path = os.path.join(ARTIFACTS_DIR, "irsim_benchmark_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_report, f, indent=2)

    print("\n=== Benchmark Report ===")
    print(json.dumps(benchmark_report, indent=2))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()