"""Automated, deterministic benchmark sweep for AI Baby.

The development window selects a configuration. Held-out test metrics are emitted
only for the selected configuration and never used for selection.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from ai_baby.search import search

BUDGETS = (1000, 5000, 20000)
TRAIN_END = 8
MAX_DEPTH = 3


def benchmark_cases():
    linear = [3 * n + 2 for n in range(12)]
    quadratic = [n * n + 1 for n in range(12)]
    fibonacci = [1, 1]
    for _ in range(10):
        fibonacci.append(fibonacci[-1] + fibonacci[-2])
    return {
        "linear_3n_plus_2": linear,
        "quadratic_n2_plus_1": quadratic,
        "fibonacci": fibonacci,
    }


def run_sweep(budgets=BUDGETS):
    results = []
    for name, sequence in benchmark_cases().items():
        configurations = []
        for budget in budgets:
            started = time.perf_counter()
            result = search(sequence, train_end=TRAIN_END, max_depth=MAX_DEPTH, budget=budget)
            elapsed = time.perf_counter() - started
            configurations.append({
                "budget": budget,
                "selected": result["selected"],
                "selected_complexity": result["selected_complexity"],
                "development": result["development"],
                "candidate_count": result["candidate_count"],
                "valid_candidate_count": result["valid_candidate_count"],
                "elapsed_seconds": round(elapsed, 3),
            })
        # Selection uses development data only; tie-break toward lower complexity,
        # then lower compute budget. Test metrics do not influence this choice.
        winner = min(configurations, key=lambda row: (
            row["development"]["mae"],
            row["selected_complexity"],
            row["budget"],
        ))
        final = search(sequence, train_end=TRAIN_END, max_depth=MAX_DEPTH, budget=winner["budget"])
        results.append({
            "benchmark": name,
            "sequence_length": len(sequence),
            "train_end_index": TRAIN_END,
            "development_points": TRAIN_END - 5,
            "held_out_test_points": len(sequence) - TRAIN_END,
            "configurations": configurations,
            "selected_configuration": winner,
            "held_out_test": final["test"],
            "baseline_last_value_test": final["baseline_test"],
            "selection_rule": "development MAE, then lower complexity, then lower budget; held-out test excluded",
        })
    return results


def render_markdown(payload):
    lines = [
        "# AI Baby — automatic improvement report",
        "",
        f"- Run UTC: {payload['run_utc']}",
        f"- Commit: `{payload['commit']}`",
        f"- Python: {payload['python']}",
        f"- Platform: {payload['platform']}",
        f"- Search depth: {payload['max_depth']}",
        f"- Budgets swept: {', '.join(map(str, payload['budgets']))}",
        "",
        "## Results",
        "",
        "| Benchmark | Selected budget | Development MAE | Held-out test MAE | Baseline test MAE | Exact test accuracy |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in payload["results"]:
        dev = item["selected_configuration"]["development"]
        test = item["held_out_test"] or {}
        baseline = item["baseline_last_value_test"] or {}
        lines.append(
            f"| {item['benchmark']} | {item['selected_configuration']['budget']} "
            f"| {dev['mae']:.6g} | {test.get('mae', float('nan')):.6g} "
            f"| {baseline.get('mae', float('nan')):.6g} "
            f"| {test.get('exact_accuracy', float('nan')):.1%} |"
        )
    lines += [
        "",
        "## Interpretation and safety",
        "",
        "- Configurations are selected using development metrics only; the held-out test is not used to choose a budget.",
        "- The quadratic benchmark is a synthetic regression sentinel, not evidence of real-world predictive ability.",
        "- Linear and Fibonacci cases are exploratory diagnostics; their scores are reported without claiming generalization.",
        "- This workflow does not modify source code or merge changes. Any proposed algorithm change requires a reviewed pull request.",
        "- Full per-configuration development metrics and selected-config test metrics are in `benchmark-report.json`.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="reports")
    parser.add_argument("--budgets", default="1000,5000,20000")
    args = parser.parse_args()
    budgets = tuple(sorted({int(v.strip()) for v in args.budgets.split(",") if v.strip()}))
    if not budgets or any(v < 1 for v in budgets):
        parser.error("Budgets must be positive integers.")
    payload = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "commit": os.environ.get("GITHUB_SHA", "local"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "max_depth": MAX_DEPTH,
        "budgets": budgets,
        "results": run_sweep(budgets),
    }
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "benchmark-report.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "benchmark-report.md").write_text(render_markdown(payload) + "\n", encoding="utf-8")
    print(render_markdown(payload))
    # Fail loudly if the canonical quadratic regression sentinel breaks.
    quadratic = next(row for row in payload["results"] if row["benchmark"] == "quadratic_n2_plus_1")
    test = quadratic["held_out_test"] or {}
    if test.get("mae") != 0.0 or test.get("exact_accuracy") != 1.0:
        print("ERROR: quadratic regression sentinel failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
