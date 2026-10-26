"""Automated, deterministic benchmark sweep for AI Baby.

Development metrics select a configuration. Held-out metrics are reported only
for that configuration and never influence the selection. Source code is never
modified automatically; algorithm changes require a reviewed pull request.
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


def next_action(item, max_budget):
    test = item["held_out_test"] or {}
    baseline = item["baseline_last_value_test"] or {}
    budget = item["selected_configuration"]["budget"]
    if test.get("mae") is None:
        return "No valid held-out result: inspect candidate evaluation and DSL coverage."
    if test["mae"] > baseline.get("mae", float("inf")):
        return "Regression versus last-value baseline: diagnose the benchmark and candidate ranking before promoting changes."
    if budget == max_budget:
        return "Best development configuration uses the budget ceiling: investigate pruning/search efficiency before increasing compute."
    return "Add independent seeds and a new held-out benchmark family before claiming generalization."


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
        # then lower compute budget. Held-out test metrics do not influence choice.
        winner = min(configurations, key=lambda row: (
            row["development"]["mae"],
            row["selected_complexity"],
            row["budget"],
        ))
        final = search(sequence, train_end=TRAIN_END, max_depth=MAX_DEPTH, budget=winner["budget"])
        item = {
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
        }
        item["next_action"] = next_action(item, max(budgets))
        results.append(item)
    return results


def render_markdown(payload):
    lines = [
        "# AI Baby — automatic improvement report",
        "",
        f"- Run UTC: {payload['run_utc']}",
        f"- Commit: `{payload['commit']}`",
        f"- Run: `{payload['run_label']}`",
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
    lines += ["", "## Diagnosi e prossima azione", ""]
    for item in payload["results"]:
        lines.append(f"- **{item['benchmark']}**: {item['next_action']}")
    lines += [
        "",
        "## Interpretazione e limiti",
        "",
        "- Le configurazioni sono selezionate usando soltanto metriche di sviluppo; il test bloccato non sceglie il budget.",
        "- Il benchmark quadratico è un controllo di regressione sintetico, non una prova di capacità predittiva nel mondo reale.",
        "- I casi lineare e Fibonacci sono diagnostici esplorativi; non autorizzano affermazioni di generalizzazione.",
        "- Il workflow non modifica il codice sorgente né integra modifiche automaticamente. Ogni cambiamento dell'algoritmo richiede una pull request revisionata.",
        "- I dettagli completi sono nel JSON allegato.",
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
    now = datetime.now(timezone.utc)
    run_number = os.environ.get("GITHUB_RUN_NUMBER", now.strftime("%Y%m%dT%H%M%SZ"))
    run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    run_label = f"{run_number}-attempt-{run_attempt}"
    payload = {
        "run_utc": now.isoformat(),
        "run_label": run_label,
        "commit": os.environ.get("GITHUB_SHA", "local"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "max_depth": MAX_DEPTH,
        "budgets": budgets,
        "results": run_sweep(budgets),
    }
    out = Path(args.output_dir)
    history = out / "history"
    history.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    markdown_text = render_markdown(payload) + "\n"
    (out / "benchmark-report.json").write_text(json_text, encoding="utf-8")
    (out / "benchmark-report.md").write_text(markdown_text, encoding="utf-8")
    (history / f"run-{run_label}.json").write_text(json_text, encoding="utf-8")
    (history / f"run-{run_label}.md").write_text(markdown_text, encoding="utf-8")
    history_index = out / "HISTORY.md"
    with history_index.open("a", encoding="utf-8") as stream:
        stream.write(f"\n## Run {run_label} — {now.isoformat()}\n\n")
        for item in payload["results"]:
            dev = item["selected_configuration"]["development"]
            test = item["held_out_test"] or {}
            stream.write(
                f"- **{item['benchmark']}** — budget {item['selected_configuration']['budget']}; "
                f"dev MAE {dev['mae']:.6g}; test MAE {test.get('mae', float('nan')):.6g}; "
                f"next: {item['next_action']}\n"
            )
    print(markdown_text)
    # Fail loudly if the canonical quadratic regression sentinel breaks.
    quadratic = next(row for row in payload["results"] if row["benchmark"] == "quadratic_n2_plus_1")
    test = quadratic["held_out_test"] or {}
    if test.get("mae") != 0.0 or test.get("exact_accuracy") != 1.0:
        print("ERROR: quadratic regression sentinel failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
