"""Daily parameter sweep for lottery heuristics; exploratory, never auto-promotes a method."""
from __future__ import annotations

import json
import hashlib
from datetime import date, datetime, timezone
from pathlib import Path

from ai_baby.lottery import GAME_RULES, load_draws_csv, rolling_origin_backtest
from ai_baby.position_decoder import chronological_position_decoder
from ai_baby.trajectory_decoder import chronological_trajectory_decoder
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
        return {"n": 0, "mean_hits": None, "p_ge2": None, "p_ge3": None, "position_exact_rate": None, "position_mae": None}
    hits = [int(r["hits"]) for r in records]
    position_errors = [
        abs(int(pred) - int(actual))
        for record in records
        for pred, actual in zip(record["prediction"], record["actual"])
    ]
    position_exact = sum(
        int(pred) == int(actual)
        for record in records
        for pred, actual in zip(record["prediction"], record["actual"])
    )
    position_count = len(records[0]["prediction"])
    by_position = []
    for rank in range(position_count):
        rank_errors = [abs(int(r["prediction"][rank]) - int(r["actual"][rank])) for r in records]
        rank_exact = sum(int(r["prediction"][rank]) == int(r["actual"][rank]) for r in records)
        by_position.append({
            "rank": rank + 1,
            "exact_rate": round(rank_exact / len(records), 6),
            "mae": round(sum(rank_errors) / len(rank_errors), 6),
        })
    return {
        "n": len(hits),
        "mean_hits": round(sum(hits) / len(hits), 6),
        "p_ge2": round(sum(h >= 2 for h in hits) / len(hits), 6),
        "p_ge3": round(sum(h >= 3 for h in hits) / len(hits), 6),
        "uniform_expected_mean_hits": round(count * count / population, 6),
        "position_exact_rate": round(position_exact / len(position_errors), 6),
        "position_mae": round(sum(position_errors) / len(position_errors), 6),
        "by_sorted_rank": by_position,
    }


def parameter_grid(run_date: str | None = None) -> dict[str, object]:
    day = date.fromisoformat(run_date) if run_date else datetime.now(timezone.utc).date()
    ordinal = day.toordinal()
    methods: dict[str, object] = {
        "global_frequency": global_frequency,
        "position_decoder_neighbours20": chronological_position_decoder(neighbours=20),
        "position_decoder_neighbours60": chronological_position_decoder(neighbours=60),
        "position_decoder_neighbours120": chronological_position_decoder(neighbours=120),
        "trajectory_window3_neighbours40": chronological_trajectory_decoder(window=3, neighbours=40),
        "trajectory_window5_neighbours60": chronological_trajectory_decoder(window=5, neighbours=60),
        "trajectory_window8_neighbours80": chronological_trajectory_decoder(window=8, neighbours=80),
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

    # Daily rotating candidates expand the search space instead of repeating only
    # the fixed anchors. The ISO date is recorded, so every sweep is reproducible.
    recent_window = 101 + (ordinal % 200)
    anti_hot_window = 101 + ((ordinal * 7) % 200)
    tau = float(1 + (ordinal % 120))
    transition_overlap = 1 + (ordinal % 4)
    transition_power = 4 + (ordinal % 7)
    gap_neighbours = 41 + (ordinal % 160)
    position_neighbours = 40 + (ordinal % 161)
    trajectory_window = 3 + (ordinal % 6)
    trajectory_neighbours = 30 + ((ordinal * 3) % 121)
    methods[f"daily_recent_window{recent_window}"] = recent_frequency(recent_window)
    methods[f"daily_anti_hot_window{anti_hot_window}"] = anti_hot(anti_hot_window)
    methods[f"daily_exponential_decay_tau{tau:g}"] = exponential_decay(tau)
    methods[f"daily_transition_overlap{transition_overlap}_power{transition_power}"] = transition_analogue(
        min_overlap=transition_overlap, power=transition_power
    )
    methods[f"daily_gap_neighbours{gap_neighbours}"] = gap_trajectory_neighbours(gap_neighbours)
    methods[f"daily_position_decoder_neighbours{position_neighbours}"] = chronological_position_decoder(neighbours=position_neighbours)
    methods[f"daily_trajectory_window{trajectory_window}_neighbours{trajectory_neighbours}"] = chronological_trajectory_decoder(window=trajectory_window, neighbours=trajectory_neighbours)
    return methods


def build_exact_rule_catalog(
    game: str,
    records_by_method: dict[str, list[dict]],
    run_date: str,
    dataset_path: str,
    dataset_sha256: str,
) -> dict:
    """Archive every historical exact full-ticket and rank-level rule hit."""
    full_exact = []
    rank_exact = []
    for method_name, records in sorted(records_by_method.items()):
        for record in records:
            prediction = [int(n) for n in record["prediction"]]
            actual = [int(n) for n in record["actual"]]
            common = {
                "method": method_name,
                "target_draw_id": record["target_draw_id"],
                "target_date": record["target_date"],
                "history_size": int(record["history_size"]),
                "prediction": prediction,
                "actual": actual,
            }
            if prediction == actual:
                full_exact.append({**common, "match_type": "all_sorted_positions_exact"})
            for rank, (predicted_number, actual_number) in enumerate(zip(prediction, actual), start=1):
                if predicted_number == actual_number:
                    rank_exact.append({
                        "method": method_name,
                        "target_draw_id": record["target_draw_id"],
                        "target_date": record["target_date"],
                        "history_size": int(record["history_size"]),
                        "rank": rank,
                        "predicted_number": predicted_number,
                        "actual_number": actual_number,
                        "full_ticket_also_exact": prediction == actual,
                    })
    full_exact.sort(key=lambda item: (item["target_date"], item["method"], item["target_draw_id"]))
    rank_exact.sort(key=lambda item: (item["target_date"], item["rank"], item["method"], item["target_draw_id"]))
    # Prioritize the trailing 12 months in the catalog while retaining the full
    # historical evidence. The cutoff is explicit and reproducible per run.
    recent_start_date = date.fromisoformat(run_date).replace(
        year=date.fromisoformat(run_date).year - 1
    ).isoformat()
    recent_full_exact = [item for item in full_exact if item["target_date"] >= recent_start_date]
    recent_rank_exact = [item for item in rank_exact if item["target_date"] >= recent_start_date]
    first_records = next(iter(records_by_method.values()), [])
    rank_count = len(first_records[0]["prediction"]) if first_records else 0
    return {
        "schema_version": 1,
        "record_type": "historical_exact_rule_catalog",
        "game": game,
        "generated_for_date_utc": run_date,
        "dataset_path": dataset_path,
        "dataset_sha256": dataset_sha256,
        "rule_count_evaluated": len(records_by_method),
        "priority_recent_period": {
            "start_date_inclusive": recent_start_date,
            "end_date_inclusive": run_date,
            "full_position_exact_matches": recent_full_exact,
            "rank_exact_matches": recent_rank_exact,
            "rank_summary": [
                {
                    "rank": rank,
                    "exact_match_count": sum(item["rank"] == rank for item in recent_rank_exact),
                    "distinct_methods_with_exact_match": sorted({
                        item["method"] for item in recent_rank_exact if item["rank"] == rank
                    }),
                }
                for rank in range(1, rank_count + 1)
            ],
        },
        "full_position_exact_matches": full_exact,
        "rank_exact_matches": rank_exact,
        "rank_summary": [
            {
                "rank": rank,
                "exact_match_count": sum(item["rank"] == rank for item in rank_exact),
                "distinct_methods_with_exact_match": sorted({
                    item["method"] for item in rank_exact if item["rank"] == rank
                }),
            }
            for rank in range(1, rank_count + 1)
        ],
        "interpretation": (
            "Keep all exact historical rule hits for later flow analysis. These are in-sample discovery results; "
            "they do not alone establish prospective predictive power."
        ),
    }


def sweep_game(csv_path: str, game: str, run_date: str, minimum_history: int = 100) -> dict:
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
    methods = parameter_grid(run_date)
    results = {}
    records_by_method = {}
    for name, predictor in methods.items():
        backtest = rolling_origin_backtest(draws, predictor, minimum_history=minimum_history)
        records = backtest["records"]
        assert isinstance(records, list)
        records_by_method[name] = records
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
    dataset_sha256 = hashlib.sha256(Path(csv_path).read_bytes()).hexdigest()
    exact_catalog = build_exact_rule_catalog(game, records_by_method, run_date, csv_path, dataset_sha256)
    catalog_dir = Path("reports/continuous")
    catalog_dir.mkdir(parents=True, exist_ok=True)
    (catalog_dir / f"exact-rule-catalog-{game}-{run_date}.json").write_text(
        json.dumps(exact_catalog, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (catalog_dir / f"exact-rule-catalog-{game}-latest.json").write_text(
        json.dumps(exact_catalog, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "exact_rule_catalog": {
            "full_position_exact_count": len(exact_catalog["full_position_exact_matches"]),
            "rank_exact_match_count": len(exact_catalog["rank_exact_matches"]),
            "dated_path": f"reports/continuous/exact-rule-catalog-{game}-{run_date}.json",
        },
        "game": game,
        "dataset": csv_path,
        "dataset_sha256": dataset_sha256,
        "draw_count_in_scored_window": len(draws) - minimum_history,
        "history_start_date": draws[0].draw_date.isoformat(),
        "first_target_date": draws[minimum_history].draw_date.isoformat(),
        "last_draw_date": draws[-1].draw_date.isoformat(),
        "minimum_history": minimum_history,
        "sweep_date_utc": run_date,
        "method_count": len(methods),
        "daily_rotating_parameters": {
            "recent_window": 101 + (date.fromisoformat(run_date).toordinal() % 200),
            "anti_hot_window": 101 + ((date.fromisoformat(run_date).toordinal() * 7) % 200),
            "decay_tau": float(1 + (date.fromisoformat(run_date).toordinal() % 120)),
            "transition_overlap": 1 + (date.fromisoformat(run_date).toordinal() % 4),
            "transition_power": 4 + (date.fromisoformat(run_date).toordinal() % 7),
            "gap_neighbours": 41 + (date.fromisoformat(run_date).toordinal() % 160),
            "position_decoder_neighbours": 40 + (date.fromisoformat(run_date).toordinal() % 161),
            "trajectory_window": 3 + (date.fromisoformat(run_date).toordinal() % 6),
            "trajectory_neighbours": 30 + ((date.fromisoformat(run_date).toordinal() * 3) % 121),
        },
        "parameter_grid": {
            "recent_windows": [10, 20, 40, 80],
            "anti_hot_windows": [10, 20, 40],
            "exponential_decay_tau": [5, 10, 20, 40],
            "transition_min_overlap": [1, 2, 3],
            "transition_power": [1, 2, 3],
            "gap_neighbours": [5, 10, 20, 40],
            "position_decoder_neighbours": [20, 60, 120] + [40 + (date.fromisoformat(run_date).toordinal() % 161)],
            "trajectory_window": [3, 5, 8, 3 + (date.fromisoformat(run_date).toordinal() % 6)],
            "trajectory_neighbours": [40, 60, 80, 30 + ((date.fromisoformat(run_date).toordinal() * 3) % 121)],
        },
        "results": results,
        "development_ranking_2023_2024_exploratory_only": ranking,
        "selection_policy": "No automatic promotion. Ranking is exploratory only; all methods remain in the report.",
        "warning": "2023-2024 and 2025+ were previously explored; neither is an untouched blind holdout. Repeated parameter sweeps inflate apparent best scores.",
    }


def write_prospective_freezes(now: datetime, outdir: Path) -> None:
    """Persist dated predictions before future draws, with input hashes and model configs."""
    from ai_baby.lottery_methods import global_frequency

    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    datasets = {
        "superenalotto": Path("data/superenalotto_snapshot_2026-10-27.csv"),
        "vincicasa": Path("data/vincicasa_snapshot_2026-10-27.csv"),
    }
    methods = {
        "chronological_trajectory_decoder_w8_n80_tau500": chronological_trajectory_decoder(
            window=8, neighbours=80, recency_tau=500.0
        ),
        "chronological_position_decoder_n120_tau500": chronological_position_decoder(
            neighbours=120, recency_tau=500.0
        ),
        "global_frequency": global_frequency,
    }
    for game, dataset in datasets.items():
        draws = load_draws_csv(dataset, game=game)
        if len(draws) < 100:
            raise ValueError(f"refusing to freeze {game}: only {len(draws)} historical draws")
        digest = hashlib.sha256(dataset.read_bytes()).hexdigest()
        predictions = {}
        for name, predictor in methods.items():
            values = tuple(sorted(int(n) for n in predictor(tuple(draws))))
            if len(values) != len(set(values)) or tuple(sorted(values)) != values:
                raise ValueError(f"{name} returned invalid prediction for {game}: {values}")
            predictions[name] = list(values)
        latest = draws[-1]
        record = {
            "schema_version": 1,
            "record_type": "prospective_prediction_freeze",
            "created_at_utc": now.isoformat(),
            "game": game,
            "target": {
                "draw_id": None,
                "draw_date": None,
                "definition": "first official draw after latest_draw; target date intentionally unknown at freeze time",
            },
            "history": {
                "dataset_path": dataset.as_posix(),
                "sha256": digest,
                "draw_count": len(draws),
                "first_draw_date": draws[0].draw_date.isoformat(),
                "latest_draw_id": latest.draw_id,
                "latest_draw_date": latest.draw_date.isoformat(),
                "latest_draw_numbers": list(latest.numbers),
            },
            "predictions": predictions,
            "evaluation_status": "pending; score only after the target draw is published",
            "scientific_warning": (
                "Exploratory lottery predictions only; this record does not establish a predictive edge "
                "or increase the known probability of winning."
            ),
        }
        dated = outdir / f"prospective-{game}-{stamp}.json"
        dated.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (outdir / f"prospective-{game}-latest.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"Frozen {game} prospective predictions: {predictions} ({dated})")


def main() -> None:
    now = datetime.now(timezone.utc)
    report = {
        "experiment": "Daily variable sweep",
        "generated_at_utc": now.isoformat(),
        "run_date_utc": now.date().isoformat(),
        "status": "exploratory; no model promotion",
        "games": {
            "superenalotto": sweep_game(
                "data/superenalotto_snapshot_2026-10-27.csv", "superenalotto", now.date().isoformat()
            ),
            "vincicasa": sweep_game(
                "data/vincicasa_snapshot_2026-10-27.csv", "vincicasa", now.date().isoformat()
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
            "| Method | All mean hits | 2023–24 hits | 2025+ hits | All position exact | All position MAE |",
            "|---|---:|---:|---:|---:|---:|",
        ])
        ranking = sorted(
            data["results"],
            key=lambda name: -(data["results"][name]["2023_2024_exploratory"]["mean_hits"] or -1),
        )
        for name in ranking:
            values = data["results"][name]
            fmt = lambda key: "n/a" if values[key]["mean_hits"] is None else f"{values[key]['mean_hits']:.4f}"
            exact = "n/a" if values["all"]["position_exact_rate"] is None else f"{values['all']['position_exact_rate']:.4f}"
            mae = "n/a" if values["all"]["position_mae"] is None else f"{values['all']['position_mae']:.3f}"
            lines.append(
                f"| {name} | {fmt('all')} | {fmt('2023_2024_exploratory')} | {fmt('2025_plus_exploratory')} | {exact} | {mae} |"
            )
        lines.append("")
    (outdir / f"{now.date().isoformat()}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (outdir / "latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_prospective_freezes(now, outdir)
    print(f"Generated daily parameter sweep for {len(report['games'])} games.")
    print(f"Methods per game: {len(parameter_grid())}; output: {outdir}")


if __name__ == "__main__":
    main()
