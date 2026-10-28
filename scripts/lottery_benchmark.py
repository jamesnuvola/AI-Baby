"""Run exploratory walk-forward benchmarks on one canonical lottery CSV."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

from ai_baby.lottery import GAME_RULES, load_draws_csv, rolling_origin_backtest, simulate_uniform_baseline
from ai_baby.lottery_methods import default_methods


def summarize(records: list[dict[str, object]], rules: dict[str, int], simulations: int, seed: int) -> dict[str, object]:
    if not records:
        return {"evaluated_draws": 0}
    hits = [int(record["hits"]) for record in records]
    actual = [record["actual"] for record in records]
    random_baseline = simulate_uniform_baseline(
        actual, rules["count"], rules["maximum"], simulations=simulations, seed=seed
    )
    distribution = Counter(hits)
    return {
        "evaluated_draws": len(records),
        "mean_hits": sum(hits) / len(hits),
        "hit_distribution": {str(k): distribution.get(k, 0) for k in range(rules["count"] + 1)},
        "p_at_least_2": sum(h >= 2 for h in hits) / len(hits),
        "p_at_least_3": sum(h >= 3 for h in hits) / len(hits) if rules["count"] >= 3 else None,
        "theoretical_uniform_mean_hits": rules["count"] ** 2 / rules["maximum"],
        "monte_carlo_uniform_mean": random_baseline["mean_hits"],
        "monte_carlo_uniform_p05": random_baseline["p05_mean_hits"],
        "monte_carlo_uniform_median": random_baseline["median_mean_hits"],
        "monte_carlo_uniform_p95": random_baseline["p95_mean_hits"],
        "monte_carlo_simulations": simulations,
        "monte_carlo_seed": seed,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", help="canonical CSV path")
    parser.add_argument("--game", choices=sorted(GAME_RULES), required=True)
    parser.add_argument("--minimum-history", type=int, default=100)
    parser.add_argument("--simulations", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20261028)
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)

    draws = load_draws_csv(args.dataset, game=args.game)
    if not draws:
        raise SystemExit("dataset has no draws for selected game")
    rules = GAME_RULES[args.game]
    result: dict[str, object] = {
        "experiment": "EXP-008 exploratory walk-forward heuristic comparison",
        "game": args.game,
        "dataset": str(Path(args.dataset)),
        "draw_count": len(draws),
        "first_draw_date": draws[0].draw_date.isoformat(),
        "last_draw_date": draws[-1].draw_date.isoformat(),
        "minimum_history": args.minimum_history,
        "selection_policy": "No model selection; all heuristics are reported as exploratory.",
        "historical_period_warning": "Historical periods may have been explored in prior research; results are not a prospective or untouched blind test.",
        "methods": {},
    }
    method_results: dict[str, object] = {}
    for name, predictor in default_methods().items():
        backtest = rolling_origin_backtest(draws, predictor, minimum_history=args.minimum_history)
        records = backtest["records"]
        assert isinstance(records, list)
        segments = {
            "all_evaluated": records,
            "validation_2023_2024": [
                r for r in records if "2023-01-01" <= str(r["target_date"]) <= "2024-12-31"
            ],
            "exploratory_2025_plus": [
                r for r in records if str(r["target_date"]) >= "2025-01-01"
            ],
        }
        method_results[name] = {
            segment: summarize(segment_records, rules, args.simulations, args.seed)
            for segment, segment_records in segments.items()
        }
    result["methods"] = method_results
    serialized = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
