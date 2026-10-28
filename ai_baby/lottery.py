"""Leakage-resistant primitives for lottery-history experiments.

The module deliberately does not claim that lottery draws are predictable.
It validates chronological data and supplies transparent scoring/baseline tools.
"""
from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Iterable, Sequence


GAME_RULES = {
    "superenalotto": {"count": 6, "minimum": 1, "maximum": 90},
    "vincicasa": {"count": 5, "minimum": 1, "maximum": 40},
}


@dataclass(frozen=True)
class Draw:
    draw_id: str
    game: str
    draw_date: date
    numbers: tuple[int, ...]


def _parse_numbers(raw: str) -> tuple[int, ...]:
    # Canonical CSV format: numbers separated by spaces, e.g. "4 12 25 48 66 81".
    tokens = raw.replace("|", " ").split()
    if not tokens:
        raise ValueError("numbers must contain at least one number")
    try:
        return tuple(int(token) for token in tokens)
    except ValueError as exc:
        raise ValueError(f"invalid number list: {raw!r}") from exc


def validate_draw(draw: Draw) -> Draw:
    game = draw.game.strip().lower()
    if game not in GAME_RULES:
        raise ValueError(f"unsupported game {draw.game!r}; expected one of {sorted(GAME_RULES)}")
    rules = GAME_RULES[game]
    if len(draw.numbers) != rules["count"]:
        raise ValueError(f"{game} requires exactly {rules['count']} main numbers")
    if len(set(draw.numbers)) != len(draw.numbers):
        raise ValueError("draw contains duplicate numbers")
    if any(n < rules["minimum"] or n > rules["maximum"] for n in draw.numbers):
        raise ValueError(f"{game} numbers must be in {rules['minimum']}..{rules['maximum']}")
    if not draw.draw_id.strip():
        raise ValueError("draw_id must not be empty")
    return Draw(draw.draw_id.strip(), game, draw.draw_date, tuple(sorted(draw.numbers)))


def load_draws_csv(path: str | Path, game: str | None = None) -> list[Draw]:
    """Load CSV with columns draw_id,date,game,numbers; date is ISO YYYY-MM-DD."""
    draws: list[Draw] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"draw_id", "date", "game", "numbers"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError(f"CSV must include columns: {', '.join(sorted(required))}")
        for row_num, row in enumerate(reader, start=2):
            try:
                row_game = (row["game"] or "").strip().lower()
                if game is not None and row_game != game.strip().lower():
                    continue
                parsed = Draw(
                    draw_id=(row["draw_id"] or "").strip(),
                    game=row_game,
                    draw_date=date.fromisoformat((row["date"] or "").strip()),
                    numbers=_parse_numbers(row["numbers"] or ""),
                )
                draws.append(validate_draw(parsed))
            except (ValueError, TypeError) as exc:
                raise ValueError(f"invalid CSV row {row_num}: {exc}") from exc

    ids = [d.draw_id for d in draws]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate draw_id found")
    if any(draws[i].draw_date > draws[i + 1].draw_date for i in range(len(draws) - 1)):
        raise ValueError("draws must be ordered chronologically by date")
    return draws


def score_prediction(prediction: Iterable[int], actual: Iterable[int], count: int, minimum: int, maximum: int) -> int:
    """Return the number of exact main-number matches after validating the prediction."""
    predicted = tuple(prediction)
    truth = set(actual)
    if len(predicted) != count or len(set(predicted)) != count:
        raise ValueError(f"prediction must contain {count} distinct numbers")
    if any(n < minimum or n > maximum for n in predicted):
        raise ValueError(f"prediction numbers must be in {minimum}..{maximum}")
    return len(set(predicted) & truth)


def uniform_expected_hits(count: int, population: int) -> float:
    """Expected overlap of two independent uniform subsets of equal size."""
    if count < 1 or population < count:
        raise ValueError("require 1 <= count <= population")
    return count * count / population


def simulate_uniform_baseline(
    actual_draws: Sequence[Sequence[int]],
    count: int,
    population: int,
    simulations: int = 1000,
    seed: int = 0,
) -> dict[str, float]:
    """Monte Carlo distribution of mean hits for uniform random predictions."""
    if not actual_draws:
        raise ValueError("actual_draws must not be empty")
    if simulations < 1:
        raise ValueError("simulations must be positive")
    rng = random.Random(seed)
    means: list[float] = []
    for _ in range(simulations):
        total = 0
        for actual in actual_draws:
            prediction = set(rng.sample(range(1, population + 1), count))
            total += len(prediction.intersection(actual))
        means.append(total / len(actual_draws))
    ordered = sorted(means)

    def percentile(p: float) -> float:
        return ordered[min(len(ordered) - 1, int((len(ordered) - 1) * p))]

    return {
        "simulations": float(simulations),
        "mean_hits": sum(means) / len(means),
        "p05_mean_hits": percentile(0.05),
        "median_mean_hits": percentile(0.50),
        "p95_mean_hits": percentile(0.95),
        "theoretical_mean_hits": uniform_expected_hits(count, population),
    }


Predictor = Callable[[Sequence[Draw]], Sequence[int]]


def rolling_origin_backtest(
    draws: Sequence[Draw],
    predictor: Predictor,
    minimum_history: int = 30,
) -> dict[str, object]:
    """Evaluate one prediction per draw using only strictly earlier draws.

    Predictor is called before each target draw is exposed. It receives a tuple
    of historical Draw objects and must return the game's main-number prediction.
    """
    if minimum_history < 1:
        raise ValueError("minimum_history must be positive")
    if len(draws) <= minimum_history:
        raise ValueError("not enough draws for the requested minimum_history")
    game = draws[0].game
    if any(d.game != game for d in draws):
        raise ValueError("backtest must contain exactly one game")
    if any(draws[i].draw_date > draws[i + 1].draw_date for i in range(len(draws) - 1)):
        raise ValueError("draws must be ordered chronologically")
    rules = GAME_RULES[game]
    records: list[dict[str, object]] = []
    for target_index in range(minimum_history, len(draws)):
        history = tuple(draws[:target_index])
        target = draws[target_index]
        prediction = tuple(predictor(history))
        hits = score_prediction(
            prediction, target.numbers, rules["count"], rules["minimum"], rules["maximum"]
        )
        records.append({
            "target_draw_id": target.draw_id,
            "target_date": target.draw_date.isoformat(),
            "history_size": len(history),
            "prediction": list(sorted(prediction)),
            "actual": list(target.numbers),
            "hits": hits,
        })
    mean_hits = sum(int(row["hits"]) for row in records) / len(records)
    return {
        "game": game,
        "minimum_history": minimum_history,
        "evaluated_draws": len(records),
        "mean_hits": mean_hits,
        "theoretical_uniform_mean_hits": uniform_expected_hits(rules["count"], rules["maximum"]),
        "records": records,
    }
