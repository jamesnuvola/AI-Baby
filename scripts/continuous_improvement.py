"""Deterministic multi-seed benchmark sweep for AI Baby.

Budget selection uses development metrics on seed 0 only. Other seeds are
robustness checks at the frozen selected budget; their test metrics never
select or tune a configuration. Source code is never modified automatically.
"""
from __future__ import annotations
import argparse, json, os, platform, sys, time
from datetime import datetime, timezone
from pathlib import Path
from ai_baby.search import search

BUDGETS = (1000, 5000, 20000)
SEEDS = (0, 1, 2)
TRAIN_END = 8
MAX_DEPTH = 3

def benchmark_cases(seed=0):
    """Deterministic sequence families; seed changes coefficients or initial values."""
    linear = [(3 + seed) * n + (2 - seed) for n in range(12)]
    quadratic = [n * n + seed * n + 1 + seed for n in range(12)]
    fibonacci = [1 + seed, 1 + seed]
    for _ in range(10):
        fibonacci.append(fibonacci[-1] + fibonacci[-2])
    geometric = [(seed + 1) * (2 ** n) for n in range(12)]
    cubic = [n ** 3 + seed for n in range(12)]
    return {"linear": linear, "quadratic": quadratic, "fibonacci": fibonacci,
            "geometric": geometric, "cubic_diagnostic": cubic}

def _metric_summary(rows, metric):
    values = [row[metric] for row in rows if row.get(metric) is not None]
    if not values:
        return {"mean": None, "worst": None, "n": 0}
    return {"mean": sum(values) / len(values), "worst": max(values), "n": len(values)}

def next_action(item, max_budget):
    test, baseline = item["aggregate_test"], item["aggregate_baseline_test"]
    budget = item["selected_configuration"]["budget"]
    if test["n"] != len(item["seeds"]):
        return "Incomplete seed coverage: inspect failed or invalid held-out evaluations."
    if test["mean"] is None:
        return "No valid held-out result: inspect candidate evaluation and DSL coverage."
    if baseline["mean"] is not None and test["mean"] > baseline["mean"]:
        return "Mean test MAE is worse than the last-value baseline: diagnose ranking and DSL coverage."
    if test["worst"] and test["worst"] > 0:
        return "At least one seed is not exact: inspect per-seed errors before claiming robust generalization."
    if budget == max_budget:
        return "Selected budget reaches the ceiling: investigate pruning/search efficiency before increasing compute."
    return "Extend to more seeds and real-world datasets; synthetic results alone do not establish generalization."

def run_sweep(budgets=BUDGETS, seeds=SEEDS):
    results = []
    base_cases = benchmark_cases(0)
    for name, base_sequence in base_cases.items():
        configurations = []
        for budget in budgets:
            started = time.perf_counter()
            result = search(base_sequence, train_end=TRAIN_END, max_depth=MAX_DEPTH, budget=budget)
            configurations.append({
                "budget": budget, "selected": result["selected"],
                "selected_complexity": result["selected_complexity"],
                "development": result["development"], "candidate_count": result["candidate_count"],
                "valid_candidate_count": result["valid_candidate_count"],
                "elapsed_seconds": round(time.perf_counter() - started, 3),
            })
        # Freeze configuration from seed-0 development metrics only.
        winner = min(configurations, key=lambda row: (
            row["development"]["mae"], row["selected_complexity"], row["budget"]))
        seed_rows = []
        for seed in seeds:
            sequence = benchmark_cases(seed)[name]
            started = time.perf_counter()
            evaluated = search(sequence, train_end=TRAIN_END, max_depth=MAX_DEPTH, budget=winner["budget"])
            seed_rows.append({
                "seed": seed, "held_out_test": evaluated["test"],
                "baseline_last_value_test": evaluated["baseline_test"],
                "selected_expression": evaluated["selected"],
                "elapsed_seconds": round(time.perf_counter() - started, 3),
            })
        test_rows = [row["held_out_test"] or {} for row in seed_rows]
        baseline_rows = [row["baseline_last_value_test"] or {} for row in seed_rows]
        test_mae = _metric_summary(test_rows, "mae")
        test_exact = _metric_summary(test_rows, "exact_accuracy")
        baseline_mae = _metric_summary(baseline_rows, "mae")
        baseline_exact = _metric_summary(baseline_rows, "exact_accuracy")
        item = {
            "benchmark": name, "sequence_length": len(base_sequence),
            "train_end_index": TRAIN_END, "development_points": TRAIN_END - 5,
            "held_out_test_points": len(base_sequence) - TRAIN_END, "seeds": list(seeds),
            "configurations": configurations, "selected_configuration": winner,
            "per_seed_results": seed_rows,
            "aggregate_test": {"mae": test_mae["mean"], "exact_accuracy": test_exact["mean"],
                               "mean": test_mae["mean"], "worst": test_mae["worst"], "n": test_mae["n"]},
            "aggregate_baseline_test": {"mae": baseline_mae["mean"], "exact_accuracy": baseline_exact["mean"],
                                        "mean": baseline_mae["mean"], "worst": baseline_mae["worst"], "n": baseline_mae["n"]},
            "selection_rule": "seed-0 development MAE, then lower complexity, then lower budget; all held-out test metrics excluded",
        }
        item["next_action"] = next_action(item, max(budgets))
        results.append(item)
    return results

def _fmt(value, spec=".6g"):
    return "n/a" if value is None else format(value, spec)

def render_markdown(payload):
    lines = [
        "# AI Baby — automatic improvement report", "",
        f"- Run UTC: {payload['run_utc']}", f"- Commit: {payload['commit']}",
        f"- Run: {payload['run_label']}", f"- Python: {payload['python']}",
        f"- Platform: {payload['platform']}", f"- Search depth: {payload['max_depth']}",
        f"- Budgets swept on seed 0: {', '.join(map(str, payload['budgets']))}",
        f"- Robustness seeds: {', '.join(map(str, payload['seeds']))}", "",
        "## Aggregate results across seeds", "",
        "| Benchmark family | Frozen budget | Mean test MAE | Worst-seed MAE | Mean exact accuracy | Baseline mean MAE |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in payload["results"]:
        test, baseline = item["aggregate_test"], item["aggregate_baseline_test"]
        lines.append(f"| {item['benchmark']} | {item['selected_configuration']['budget']} "
                     f"| {_fmt(test['mean'])} | {_fmt(test['worst'])} "
                     f"| {_fmt(test['exact_accuracy'], '.1%')} | {_fmt(baseline['mean'])} |")
    lines += ["", "## Per-family diagnosis and next action", ""]
    for item in payload["results"]:
        lines.append(f"- **{item['benchmark']}**: {item['next_action']}")
    lines += [
        "", "## Method and limitations", "",
        "- Budget is selected using seed-0 development metrics only; held-out test results do not select the configuration.",
        "- The selected budget is frozen for all robustness seeds in that family.",
        "- Families include linear, quadratic, Fibonacci, geometric, and cubic diagnostic sequences.",
        "- Synthetic seeds are coefficient/initial-value variants, not independent real-world datasets.",
        "- The cubic case is diagnostic: failure is recorded as a limitation, not hidden or used to tune against the test set.",
        "- The workflow does not modify the search engine or merge algorithm changes automatically; changes require reviewed pull requests.",
        "- Full per-seed metrics and timing are available in the JSON report.", "",
    ]
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="reports")
    parser.add_argument("--budgets", default="1000,5000,20000")
    parser.add_argument("--seeds", default="0,1,2")
    args = parser.parse_args()
    budgets = tuple(sorted({int(v.strip()) for v in args.budgets.split(",") if v.strip()}))
    seeds = tuple(sorted({int(v.strip()) for v in args.seeds.split(",") if v.strip()}))
    if not budgets or any(v < 1 for v in budgets):
        parser.error("Budgets must be positive integers.")
    if not seeds or 0 not in seeds or any(v < 0 for v in seeds):
        parser.error("Seeds must be non-negative integers and include seed 0 for budget selection.")
    now = datetime.now(timezone.utc)
    run_number = os.environ.get("GITHUB_RUN_NUMBER", now.strftime("%Y%m%dT%H%M%SZ"))
    run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    run_label = f"{run_number}-attempt-{run_attempt}"
    payload = {"run_utc": now.isoformat(), "run_label": run_label,
               "commit": os.environ.get("GITHUB_SHA", "local"), "python": sys.version.split()[0],
               "platform": platform.platform(), "max_depth": MAX_DEPTH,
               "budgets": budgets, "seeds": seeds, "results": run_sweep(budgets, seeds)}
    out = Path(args.output_dir)
    history = out / "history"
    history.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    markdown_text = render_markdown(payload) + "\n"
    (out / "benchmark-report.json").write_text(json_text, encoding="utf-8")
    (out / "benchmark-report.md").write_text(markdown_text, encoding="utf-8")
    (history / f"run-{run_label}.json").write_text(json_text, encoding="utf-8")
    (history / f"run-{run_label}.md").write_text(markdown_text, encoding="utf-8")
    with (out / "HISTORY.md").open("a", encoding="utf-8") as stream:
        stream.write(f"\n## Run {run_label} — {now.isoformat()}\n\n")
        for item in payload["results"]:
            test = item["aggregate_test"]
            stream.write(f"- **{item['benchmark']}** — frozen budget {item['selected_configuration']['budget']}; "
                         f"mean test MAE {_fmt(test['mean'])}; worst-seed MAE {_fmt(test['worst'])}; "
                         f"next: {item['next_action']}\n")
    print(markdown_text)
    quadratic = next(row for row in payload["results"] if row["benchmark"] == "quadratic")
    test = quadratic["aggregate_test"]
    if test["mean"] != 0.0 or test["exact_accuracy"] != 1.0:
        print("ERROR: quadratic multi-seed regression sentinel failed.", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
