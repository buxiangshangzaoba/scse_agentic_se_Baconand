import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime



from analyst_agent import run_analyst
from planner_agent import run_planner
from developer_agent import run_developer, run_developer_revision
from test_agent import run_test_agent
from runner import run_simulation
from reviewer_agent import run_reviewer
from reviewer_benchmark_agent import run_reviewer_benchmark



LOG_FILE = "trace.log"


def log(event):
    """Append a timestamped event to trace.log and print it."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {event}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


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


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)



def main():
    ensure_dirs()

    
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")

    log("=== Pipeline started ===")

    
    log("Loading brief ...")
    with open("brief.txt", "r", encoding="utf-8") as f:
        brief_text = f.read()
    log(f"Loaded brief.txt ({len(brief_text)} chars)")

    log("Running Analyst Agent ...")
    requirements = run_analyst(brief_text)
    save_json("artifacts/requirements.json", requirements)
    log("Analyst Agent created artifacts/requirements.json")

    log("Running Planner Agent ...")
    plan = run_planner(requirements)
    save_json("artifacts/plan.json", plan)
    log("Planner Agent created artifacts/plan.json")

    log("Running Developer Agent ...")
    nav_code = run_developer(plan)
    save_text("generated/navigation_logic.py", nav_code)
    save_text("artifacts/navigation_logic.py", nav_code)
    log("Developer Agent created generated/navigation_logic.py")

 
    log("Running Test Agent ...")
    test_code = run_test_agent(requirements, plan)
    save_text("tests/test_navigation_logic.py", test_code)
    log("Test Agent created tests/test_navigation_logic.py")

    
    log("Running Simulation Runner ...")
    sim_report = run_simulation()
    save_json("artifacts/simulation_report.json", sim_report)
    log(f"Simulation Runner created artifacts/simulation_report.json "
        f"(passed={sim_report['passed']}/{sim_report['total_scenarios']})")

    log("Running Reviewer Agent (simulation) ...")
    review = run_reviewer(sim_report)
    save_json("artifacts/review_result.json", review)
    log(f"Reviewer Agent created artifacts/review_result.json "
        f"(needs_revision={review['needs_revision']})")

   
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

    bench_report = load_json("artifacts/irsim_benchmark_report.json")
    log(f"Benchmark report loaded: success_rate={bench_report['success_rate']}, "
        f"efficiency_rate={bench_report['efficiency_rate']}")

  
    log("Running Benchmark Reviewer ...")
    bench_review = run_reviewer_benchmark(bench_report)
    save_json("artifacts/benchmark_review.json", bench_review)
    log(f"Benchmark Reviewer created artifacts/benchmark_review.json "
        f"(needs_revision={bench_review['needs_revision']})")

    needs_revision = review.get("needs_revision", False) or \
                     bench_review.get("needs_revision", False)

    if needs_revision:
        log("Revision needed — running Developer Revision ...")
        revised_code = run_developer_revision(
            original_code=nav_code,
            review_notes=review,
            benchmark_report=bench_report,
            requirements=requirements,
            plan=plan,
        )
        save_text("generated/navigation_logic_v2.py", revised_code)
        save_text("artifacts/navigation_logic_v2.py", revised_code)
        log("Developer Revision created generated/navigation_logic_v2.py")

        shutil.copy("generated/navigation_logic.py",
                    "generated/navigation_logic_v1_backup.py")
        shutil.copy("generated/navigation_logic_v2.py",
                    "generated/navigation_logic.py")
        log("Swapped in revised navigation_logic.py")

        log("Re-running Simulation Runner on revised logic ...")
        sim_report_v2 = run_simulation()
        save_json("artifacts/simulation_report_v2.json", sim_report_v2)
        log(f"Simulation (revised) created artifacts/simulation_report_v2.json "
            f"(passed={sim_report_v2['passed']}/{sim_report_v2['total_scenarios']})")

        log("Re-running IR-SIM Benchmark on revised logic ...")
        result = subprocess.run(
            [sys.executable, "benchmark_irsim.py"],
            capture_output=True, text=True, timeout=1800,
        )
        if result.returncode != 0:
            log(f"Re-run IR-SIM Benchmark FAILED: {result.stderr[-500:]}")
            raise RuntimeError("Re-run IR-SIM Benchmark failed")
        log("Re-run IR-SIM Benchmark created artifacts/irsim_benchmark_report.json")

        bench_report_v2 = load_json("artifacts/irsim_benchmark_report.json")
        bench_review_v2 = run_reviewer_benchmark(bench_report_v2)
        save_json("artifacts/benchmark_review_v2.json", bench_review_v2)
        log(f"Benchmark Reviewer (revised) created artifacts/benchmark_review_v2.json "
            f"(needs_revision={bench_review_v2['needs_revision']})")
    else:
        log("No revision needed — skipping Developer Revision step.")

    log("=== Pipeline finished successfully ===")


if __name__ == "__main__":
    main()