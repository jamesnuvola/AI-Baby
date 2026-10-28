"""Chronological rank-position decoder for sorted lottery outcomes.

This is a deliberately non-standard research hypothesis, not a claim of
predictability. Each historical draw is a sorted state; its chronological
successor is the target. Similar prior states vote separately for each sorted
rank, then dynamic programming enforces a valid strictly increasing ticket.
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Sequence

from .lottery import Draw, GAME_RULES


def _state_features(numbers: Sequence[int], population: int) -> tuple[float, ...]:
    ordered = tuple(sorted(numbers))
    gaps = (ordered[0],) + tuple(
        ordered[i] - ordered[i - 1] for i in range(1, len(ordered))
    ) + (population + 1 - ordered[-1],)
    # Rank values preserve positional identity; gaps describe local geometry.
    scale = float(population + 1)
    return tuple(n / scale for n in ordered) + tuple(g / scale for g in gaps)


def chronological_position_decoder(neighbours: int = 60, recency_tau: float = 500.0):
    """Predict sorted rank positions from analogous historical states and successors.

    For each historical state t, compare its rank/gap signature with the latest
    observed state. The successor at t+1 contributes a distance- and recency-
    weighted vote to each sorted rank independently. A small empirical
    rank-specific prior stabilizes sparse votes. A monotone dynamic program then
    selects the highest-scoring strictly increasing sequence.
    """
    if neighbours < 1:
        raise ValueError("neighbours must be positive")
    if recency_tau <= 0:
        raise ValueError("recency_tau must be positive")

    def predict(history: Sequence[Draw]) -> tuple[int, ...]:
        if len(history) < 3:
            raise ValueError("chronological_position_decoder requires at least three draws")
        game = history[-1].game
        rules = GAME_RULES[game]
        count, population = rules["count"], rules["maximum"]
        latest = tuple(sorted(history[-1].numbers))
        current_features = _state_features(latest, population)
        candidates: list[tuple[float, int]] = []
        for index in range(len(history) - 1):
            features = _state_features(history[index].numbers, population)
            distance = sum(abs(a - b) for a, b in zip(current_features, features))
            age = len(history) - 2 - index
            weight = math.exp(-4.0 * distance) * math.exp(-age / recency_tau)
            candidates.append((weight, index))
        candidates.sort(key=lambda item: (-item[0], -item[1]))
        selected = candidates[: min(neighbours, len(candidates))]

        scores = [
            {number: 1e-9 for number in range(1, population + 1)}
            for _ in range(count)
        ]
        # Rank-specific empirical prior, deliberately weaker than analogue votes.
        prior_weight = 0.02
        for rank in range(count):
            frequencies = Counter(draw.numbers[rank] for draw in history)
            for number, frequency in frequencies.items():
                scores[rank][number] += prior_weight * frequency / len(history)
        for weight, index in selected:
            successor = tuple(sorted(history[index + 1].numbers))
            for rank, number in enumerate(successor):
                scores[rank][number] += weight

        # DP maximizes summed log score subject to n[0] < ... < n[k-1].
        dp: list[dict[int, float]] = []
        parents: list[dict[int, int | None]] = []
        first = {n: math.log(scores[0][n]) for n in range(1, population + 1)}
        dp.append(first)
        parents.append({n: None for n in range(1, population + 1)})
        for rank in range(1, count):
            previous = dp[-1]
            best_score = -math.inf
            best_number: int | None = None
            current_scores: dict[int, float] = {}
            current_parents: dict[int, int | None] = {}
            for number in range(1, population + 1):
                smaller = number - 1
                if smaller in previous and previous[smaller] > best_score:
                    best_score = previous[smaller]
                    best_number = smaller
                if best_number is not None:
                    current_scores[number] = math.log(scores[rank][number]) + best_score
                    current_parents[number] = best_number
            dp.append(current_scores)
            parents.append(current_parents)

        final_number = max(dp[-1], key=dp[-1].get)
        result = [final_number]
        for rank in range(count - 1, 0, -1):
            parent = parents[rank][result[-1]]
            if parent is None:
                raise RuntimeError("position decoder failed to reconstruct a valid ticket")
            result.append(parent)
        return tuple(reversed(result))

    return predict
