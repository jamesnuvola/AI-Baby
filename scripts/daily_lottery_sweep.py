"""Daily parameter sweep for lottery heuristics; exploratory, never auto-promotes a method."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ai_baby.lottery import GAME_RULES, load_draws_csv, rolling_origin_backtest
from ai_baby.lottery_methods import (
    anti_hot,
    exponential_decay,
    gap_trajectory_neighbours,
    global_frequency,
    overdue_first,
    random_uniform,
    recent_frequency,
    transition_analogue,
)


def metric(records: list[dict], count: int, population: int) -> dict:
    if not records:
        return {"n": 0, "mean_hits": None, "p_ge2": None, "p_ge3": None}
    hits = [int(r["hits"]) for r in records]
    return {
        "n": len(hits),
        "mean_hits": round(sum(hits) / len(hits), 6),
        "p_ge2": round(sum(h >= 2 for h in hits) / len(hits), 6),
        "p_ge3": round(sum(h >= 3 for h in hits) / len(hits), 6),
        "uniform_expected_mean_hits": round(count * count / population, 6),
    }


def parameter_grid() -> dict[str, object]:
    methods: dict[str, object] = {
        "global_frequency": global_frequency,
        "overdue_first": overdue_first,
        "random_uniform_seed0": random_uniform(0),
    }
    for window in (10, 20, 40, 80):
        methods[f"recent_frequency_window{window}"] = recent_frequency(window)
    for window in (10, 20, 40):
        methods[f"anti_hot_window{window}"] = anti_hot(window)
    for tau in (5.0, 10.0, 20.0, 40.0):
        methods[f"exponential_decay_tau{tau:g}"] = exponential_decay(tau)
    for overlap in (1, 2, 3):
        for power in (1, 2, 3):
            methods[f"transition_overlap{overlap}_power{power}"] = transition_analogue(
                min_overlap=overlap, power=power
            )
    for neighbours in (5, 10, 20, 40):
        methods[f"gap_neighbours{neighbours}"] = gap_trajectory_neighbours(neighbours)
    return methods


def sweep_game(csv_path: str, game: str, minimum_history: int = 100) -> dict:
    draws = load_draws_csv(csv_path, game=game)
    if len(draws) <= minimum_history:
        raise ValueError(f"not enough {game} draws for minimum_history={minimum_history}")
    # Bound daily runtime while preserving a meaningful rolling-origin window.
    # Keep 100 pre-2022 draws as warm-up, then score target draws from 2022 onward.
    first_target_index = next(
        (i for i, draw in enumerate(draws) if draw.draw_date.isoformat() >= "2022-01-01"),
        None,
    )
    if first_target_index is None or first_target_index < minimum_history:
        raise ValueError(f"not enough pre-2022 warm-up history for {game}")
    draws = draws[first_target_index - minimum_history:]
    rules = GAME_RULES[game]
    methods = parameter_grid()
    results = {}
    for name, predictor in methods.items():
        backtest = rolling_origin_backtest(draws, predictor, minimum_history=minimum_history)
        records = backtest["records"]
        assert isinstance(records, list)
        segments = {
            "all": records,
            "2023_2024_exploratory": [
                r for r in records if "2023-01-01" <= str(r["target_date"]) <= "2024-12-31"
            ],
            "2025_plus_exploratory": [r for r in records if str(r["target_date"]) >= "2025-01-01"],
        }
        results[name] = {
            segment: metric(rows, rules["count"], rules["maximum"])
            for segment, rows in segments.items()
        }
    # This ranking is descriptive only. It is never used to change default_methods().
    ranking = sorted(
        results,
        key=lambda name: (
            -(results[name]["2023_2024_exploratory"]["mean_hits"] or -1),
            name,
        ),
    )
    return {
        "game": game,
        "dataset": csv_path,
        "draw_count_in_scored_window": len(draws) - minimum_history,
        "history_start_date": draws[0].draw_date.isoformat(),
        "first_target_date": draws[minimum_history].draw_date.isoformat(),
        "last_draw_date": draws[-1].draw_date.isoformat(),
        "minimum_history": minimum_history,
        "method_count": len(methods),
        "parameter_grid": {
            "recent_windows": [10, 20, 40, 80],
            "anti_hot_windows": [10, 20, 40],
            "exponential_decay_tau": [5, 10, 20, 40],
            "transition_min_overlap": [1, 2, 3],
            "transition_power": [1, 2, 3],
            "gap_neighbours": [5, 10, 20, 40],
        },
        "results": results,
        "development_ranking_2023_2024_exploratory_only": ranking,
        "selection_policy": "No automatic promotion. Ranking is exploratory only; all methods remain in the report.",
        "warning": "2023-2024 and 2025+ were previously explored; neither is an untouched blind holdout. Repeated parameter sweeps inflate apparent best scores.",
    }


def main() -> None:
    now = datetime.now(timezone.utc)
    report = {
        "experiment": "Daily variable sweep",
        "generated_at_utc": now.isoformat(),
        "run_date_utc": now.date().isoformat(),
        "status": "exploratory; no model promotion",
        "games": {
            "superenalotto": sweep_game(
                "data/superenalotto_snapshot_2026-10-27.csv", "superenalotto"
            ),
            "vincicasa": sweep_game(
                "data/vincicasa_snapshot_2026-10-27.csv", "vincicasa"
            ),
        },
        "next_required_step": "Refresh official source data and score frozen prospective predictions before claiming any edge.",
    }
    outdir = Path("reports/continuous")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"{now.date().isoformat()}.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (outdir / "latest.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        f"# Daily variable sweep — {now.date().isoformat()}",
        "",
        f"Generated: {now.isoformat()}",
        "",
        "**Status:** exploratory. No method is promoted automatically.",
        "",
        "Historical segments below were previously explored and are not blind holdouts. Repeated sweeps create multiple-comparison bias.",
        "",
    ]
    for game, data in report["games"].items():
        lines.extend([
            f"## {game}",
            "",
            f"Scored targets: {data['draw_count_in_scored_window']}; history starts {data['history_start_date']}; first target {data['first_target_date']}; latest draw {data['last_draw_date']}.",
            "",
            "| Method | All mean hits | 2023–24 mean hits | 2025+ mean hits |",
            "|---|---:|---:|---:|",
        ])
        ranking = sorted(
            data["results"],
            key=lambda name: -(data["results"][name]["2023_2024_exploratory"]["mean_hits"] or -1),
        )
        for name in ranking:
            values = data["results"][name]
            fmt = lambda key: "n/a" if values[key]["mean_hits"] is None else f"{values[key]['mean_hits']:.4f}"
            lines.append(
                f"| {name} | {fmt('all')} | {fmt('2023_2024_exploratory')} | {fmt('2025_plus_exploratory')} |"
            )
        lines.append("")
    (outdir / f"{now.date().isoformat()}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (outdir / "latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated daily parameter sweep for {len(report['games'])} games.")
    print(f"Methods per game: {len(parameter_grid())}; output: {outdir}")


if __name__ == "__main__":
    main()
