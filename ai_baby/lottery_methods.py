"""Transparent and deliberately diverse lottery-number ranking heuristics."""
from __future__ import annotations

import random
from collections import Counter
from typing import Sequence

from .lottery import Draw, GAME_RULES


def _rank(scores: dict[int, float], count: int) -> tuple[int, ...]:
    # Explicit deterministic tie-break makes runs reproducible.
    return tuple(sorted(scores, key=lambda n: (-scores[n], n))[:count])


def global_frequency(history: Sequence[Draw]) -> tuple[int, ...]:
    game = history[-1].game
    rules = GAME_RULES[game]
    counts = Counter(n for draw in history for n in draw.numbers)
    scores = {n: float(counts[n]) for n in range(rules["minimum"], rules["maximum"] + 1)}
    return _rank(scores, rules["count"])


def recent_frequency(window: int = 20):
    if window < 1:
        raise ValueError("window must be positive")

    def predict(history: Sequence[Draw]) -> tuple[int, ...]:
        game = history[-1].game
        rules = GAME_RULES[game]
        counts = Counter(n for draw in history[-window:] for n in draw.numbers)
        scores = {n: float(counts[n]) for n in range(rules["minimum"], rules["maximum"] + 1)}
        return _rank(scores, rules["count"])
    return predict


def anti_hot(window: int = 20):
    """Counter-intuitive control: prefer numbers least frequent in the recent window."""
    if window < 1:
        raise ValueError("window must be positive")

    def predict(history: Sequence[Draw]) -> tuple[int, ...]:
        game = history[-1].game
        rules = GAME_RULES[game]
        counts = Counter(n for draw in history[-window:] for n in draw.numbers)
        scores = {n: -float(counts[n]) for n in range(rules["minimum"], rules["maximum"] + 1)}
        return _rank(scores, rules["count"])
    return predict


def exponential_decay(tau: float = 10.0):
    """Recency-weighted frequency; latest draw has weight 1, older draws decay exponentially."""
    if tau <= 0:
        raise ValueError("tau must be positive")

    def predict(history: Sequence[Draw]) -> tuple[int, ...]:
        game = history[-1].game
        rules = GAME_RULES[game]
        scores = {n: 0.0 for n in range(rules["minimum"], rules["maximum"] + 1)}
        for age, draw in enumerate(reversed(history)):
            weight = 2.0 ** (-age / tau)
            for number in draw.numbers:
                scores[number] += weight
        return _rank(scores, rules["count"])
    return predict


def overdue_first(history: Sequence[Draw]) -> tuple[int, ...]:
    """Counter-intuitive control: rank numbers by draws since their last appearance."""
    game = history[-1].game
    rules = GAME_RULES[game]
    last_seen = {n: len(history) + 1 for n in range(rules["minimum"], rules["maximum"] + 1)}
    for age, draw in enumerate(reversed(history)):
        for number in draw.numbers:
            if last_seen[number] == len(history) + 1:
                last_seen[number] = age
    scores = {n: float(last_seen[n]) for n in last_seen}
    return _rank(scores, rules["count"])


def random_uniform(seed: int = 0):
    """Stateful uniform random ticket stream; seed must be recorded in the report."""
    rng = random.Random(seed)

    def predict(history: Sequence[Draw]) -> tuple[int, ...]:
        game = history[-1].game
        rules = GAME_RULES[game]
        return tuple(sorted(rng.sample(range(rules["minimum"], rules["maximum"] + 1), rules["count"])))
    return predict


def default_methods() -> dict[str, object]:
    return {
        "global_frequency": global_frequency,
        "recent_frequency_20": recent_frequency(20),
        "anti_hot_20": anti_hot(20),
        "exponential_decay_tau10": exponential_decay(10.0),
        "overdue_first": overdue_first,
        "random_uniform_seed0": random_uniform(0),
        "transition_analogue_overlap2_power3": transition_analogue(min_overlap=2, power=3),
        "gap_trajectory_nearest20": gap_trajectory_neighbours(neighbours=20),
    }


def transition_analogue(min_overlap: int = 2, power: int = 3):
    """Vote for successor numbers of historical draws resembling the latest draw."""
    if min_overlap < 0 or power < 1:
        raise ValueError("min_overlap must be nonnegative and power positive")

    def predict(history: Sequence[Draw]) -> tuple[int, ...]:
        if len(history) < 2:
            raise ValueError("transition_analogue requires at least two historical draws")
        game = history[-1].game
        rules = GAME_RULES[game]
        current = set(history[-1].numbers)
        scores = {n: 0.0 for n in range(rules["minimum"], rules["maximum"] + 1)}
        for index in range(len(history) - 1):
            overlap = len(current.intersection(history[index].numbers))
            if overlap >= min_overlap:
                weight = float(overlap ** power)
                for number in history[index + 1].numbers:
                    scores[number] += weight
        if not any(scores.values()):
            return global_frequency(history)
        return _rank(scores, rules["count"])
    return predict


def _gap_signature(numbers: Sequence[int], population: int) -> tuple[int, ...]:
    ordered = sorted(numbers)
    boundaries = [0, *ordered, population + 1]
    return tuple(boundaries[i + 1] - boundaries[i] for i in range(len(boundaries) - 1))


def gap_trajectory_neighbours(neighbours: int = 20):
    """Find prior states with similar gap geometry, then vote for their successors."""
    if neighbours < 1:
        raise ValueError("neighbours must be positive")

    def predict(history: Sequence[Draw]) -> tuple[int, ...]:
        if len(history) < 2:
            raise ValueError("gap_trajectory_neighbours requires at least two historical draws")
        game = history[-1].game
        rules = GAME_RULES[game]
        current_signature = _gap_signature(history[-1].numbers, rules["maximum"])
        candidates: list[tuple[int, int]] = []
        for index in range(len(history) - 1):
            signature = _gap_signature(history[index].numbers, rules["maximum"])
            distance = sum(abs(a - b) for a, b in zip(current_signature, signature))
            candidates.append((distance, index))
        candidates.sort(key=lambda item: (item[0], item[1]))
        scores = {n: 0.0 for n in range(rules["minimum"], rules["maximum"] + 1)}
        for distance, index in candidates[:neighbours]:
            weight = 1.0 / (1.0 + distance)
            for number in history[index + 1].numbers:
                scores[number] += weight
        if not any(scores.values()):
            return global_frequency(history)
        return _rank(scores, rules["count"])
    return predict
