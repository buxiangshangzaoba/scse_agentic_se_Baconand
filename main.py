import json
import os
import subprocess
import sys
import time
from datetime import datetime


## Import all the necessary functions from other modules.
from analyst_agent import run_analyst
from planner_agent import run_planner
from developer_agent import run_developer
from test_agent import run_test_agent
from runner import run_simulation
from reviewer_agent import run_reviewer
from reviewer_benchmark_agent import run_reviewer_benchmark


# ---------- Logging ----------
LOG_FILE = "trace.log"


def log(event):
    """Append a timestamped event to trace.log and print it."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {event}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ---------- Helpers ----------
def ensure_dirs():
    os.makedirs("artifacts", exist_ok=True)
    os.makedirs("generated", exist_ok=True)
    os.makedirs("tests", exist_ok=True)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# ---------- Main pipeline ----------
def main():
    ensure_dirs()

    # Reset log at the start of each run
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")

    log("=== Pipeline started ===")

    # 1. Load brief
    log("Loading brief ...")
    with open("brief.txt", "r", encoding="utf-8") as f:
        brief_text = f.read()
    log(f"Loaded brief.txt ({len(brief_text)} chars)")

    # 2. Analyst Agent
    log("Running Analyst Agent ...")
    requirements = run_analyst(brief_text)
    save_json("artifacts/requirements.json", requirements)
    log("Analyst Agent created artifacts/requirements.json")

    # 3. Planner Agent
    log("Running Planner Agent ...")
    plan = run_planner(requirements)
    save_json("artifacts/plan.json", plan)
    log("Planner Agent created artifacts/plan.json")

    # 4. Developer Agent
    log("Running Developer Agent ...")
    nav_code = run_developer(plan)
    save_text("generated/navigation_logic.py", nav_code)
    # Also mirror into artifacts for reference
    save_text("artifacts/navigation_logic.py", nav_code)
    log("Developer Agent created generated/navigation_logic.py")

    # 5. Test Agent
    log("Running Test Agent ...")
    test_code = run_test_agent(requirements, plan)
    save_text("tests/test_navigation_logic.py", test_code)
    log("Test Agent created tests/test_navigation_logic.py")

    # 6. Simulation Runner
    log("Running Simulation Runner ...")
    sim_report = run_simulation()
    save_json("artifacts/simulation_report.json", sim_report)
    log(f"Simulation Runner created artifacts/simulation_report.json "
        f"(passed={sim_report['passed']}/{sim_report['total_scenarios']})")

    # 7. Reviewer Agent (simulation)
    log("Running Reviewer Agent (simulation) ...")
    review = run_reviewer(sim_report)
    save_json("artifacts/review_result.json", review)
    log(f"Reviewer Agent created artifacts/review_result.json "
        f"(needs_revision={review['needs_revision']})")

    # 8. IR-SIM Benchmark
    log("Running IR-SIM Benchmark ...")
    result = subprocess.run(
        [sys.executable, "benchmark_irsim.py"],
        capture_output=True, text=True, timeout=1800,
    )
    print(result.stdout[-2000:])
    if result.returncode != 0:
        log(f"IR-SIM Benchmark FAILED: {result.stderr[-500:]}")
        raise RuntimeError("IR-SIM Benchmark failed")
    log("IR-SIM Benchmark created artifacts/irsim_benchmark_report.json")

    # Load benchmark report for the next step
    with open("artifacts/irsim_benchmark_report.json", "r", encoding="utf-8") as f:
        bench_report = json.load(f)
    log(f"Benchmark report loaded: success_rate={bench_report['success_rate']}, "
        f"efficiency_rate={bench_report['efficiency_rate']}")

    # 9. Benchmark Reviewer
    log("Running Benchmark Reviewer ...")
    bench_review = run_reviewer_benchmark(bench_report)
    save_json("artifacts/benchmark_review.json", bench_review)
    log(f"Benchmark Reviewer created artifacts/benchmark_review.json "
        f"(needs_revision={bench_review['needs_revision']})")

    log("=== Pipeline finished successfully ===")


if __name__ == "__main__":
    main()