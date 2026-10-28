"""Multi-step chronological trajectory analogues for sorted rank positions."""
from __future__ import annotations

import math
from collections import Counter
from typing import Sequence

from .lottery import Draw, GAME_RULES
from .position_decoder import _state_features


def chronological_trajectory_decoder(window: int = 5, neighbours: int = 60, recency_tau: float = 500.0):
    """Match whole recent trajectories, including velocity and acceleration.

    Unlike a single-state nearest-neighbour model, this compares a window of
    successive sorted-rank/gap states. Similar past trajectories vote with the
    rank positions of the draw immediately following the matched trajectory.
    """
    if window < 2:
        raise ValueError("window must be at least 2")
    if neighbours < 1:
        raise ValueError("neighbours must be positive")
    if recency_tau <= 0:
        raise ValueError("recency_tau must be positive")

    def predict(history: Sequence[Draw]) -> tuple[int, ...]:
        if len(history) < window + 1:
            raise ValueError(f"trajectory decoder requires at least {window + 1} draws")
        game = history[-1].game
        rules = GAME_RULES[game]
        count, population = rules["count"], rules["maximum"]
        vectors = [_state_features(draw.numbers, population) for draw in history]
        target = vectors[-window:]
        target_velocity = [tuple(target[i][j] - target[i-1][j] for j in range(len(target[i]))) for i in range(1, window)]
        target_acceleration = [
            tuple(target_velocity[i][j] - target_velocity[i-1][j] for j in range(len(target_velocity[i])))
            for i in range(1, len(target_velocity))
        ]
        candidates: list[tuple[float, int]] = []
        for end in range(window - 1, len(history) - 1):
            past = vectors[end-window+1:end+1]
            state_distance = sum(
                abs(a-b)
                for actual, analogue in zip(target, past)
                for a, b in zip(actual, analogue)
            ) / (window * len(target[0]))
            velocity = [
                tuple(past[i][j] - past[i-1][j] for j in range(len(past[i])))
                for i in range(1, window)
            ]
            velocity_distance = sum(
                abs(a-b)
                for actual, analogue in zip(target_velocity, velocity)
                for a, b in zip(actual, analogue)
            ) / (len(target_velocity) * len(target[0]))
            acceleration_distance = 0.0
            if target_acceleration:
                acceleration = [
                    tuple(velocity[i][j] - velocity[i-1][j] for j in range(len(velocity[i])))
                    for i in range(1, len(velocity))
                ]
                acceleration_distance = sum(
                    abs(a-b)
                    for actual, analogue in zip(target_acceleration, acceleration)
                    for a, b in zip(actual, analogue)
                ) / (len(target_acceleration) * len(target[0]))
            distance = state_distance + 1.5 * velocity_distance + 0.75 * acceleration_distance
            age = len(history) - 2 - end
            weight = math.exp(-5.0 * distance) * math.exp(-age / recency_tau)
            candidates.append((weight, end))
        candidates.sort(key=lambda item: (-item[0], -item[1]))
        selected = candidates[:min(neighbours, len(candidates))]
        scores = [{n: 1e-9 for n in range(1, population + 1)} for _ in range(count)]
        # Weak rank prior; most of the signal must come from trajectory analogues.
        for rank in range(count):
            frequencies = Counter(draw.numbers[rank] for draw in history)
            for number, frequency in frequencies.items():
                scores[rank][number] += 0.01 * frequency / len(history)
        for weight, end in selected:
            successor = tuple(sorted(history[end+1].numbers))
            for rank, number in enumerate(successor):
                scores[rank][number] += weight

        # Viterbi-style monotonic decoding ensures a valid sorted ticket.
        dp = [{n: math.log(scores[0][n]) for n in range(1, population + 1)}]
        parents: list[dict[int, int | None]] = [{n: None for n in range(1, population + 1)}]
        for rank in range(1, count):
            current: dict[int, float] = {}
            parent_map: dict[int, int | None] = {}
            best_score = -math.inf
            best_number = None
            for number in range(1, population + 1):
                smaller = number - 1
                if smaller in dp[-1] and dp[-1][smaller] > best_score:
                    best_score, best_number = dp[-1][smaller], smaller
                if best_number is not None:
                    current[number] = math.log(scores[rank][number]) + best_score
                    parent_map[number] = best_number
            dp.append(current)
            parents.append(parent_map)
        final_number = max(dp[-1], key=dp[-1].get)
        result = [final_number]
        for rank in range(count - 1, 0, -1):
            result.append(parents[rank][result[-1]])
        return tuple(reversed(result))

    return predict
