"""Freeze pre-draw predictions from every registered method for prospective shadow evaluation."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Sequence

from ai_baby.lottery import Draw, GAME_RULES, load_draws_csv
from ai_baby.lottery_methods import default_methods


def build_freeze(
    draws: Sequence[Draw],
    target_date: str,
    frozen_at: str,
    code_revision: str,
) -> dict[str, object]:
    if not draws:
        raise ValueError("draws must not be empty")
    game = draws[0].game
    if any(draw.game != game for draw in draws):
        raise ValueError("freeze must contain one game only")
    if draws[-1].draw_date.isoformat() >= target_date:
        raise ValueError("target_date must be later than the latest draw in the dataset")
    # Require an explicit timezone so the freeze can be audited.
    parsed_timestamp = datetime.fromisoformat(frozen_at)
    if parsed_timestamp.tzinfo is None or parsed_timestamp.utcoffset() is None:
        raise ValueError("frozen_at must include a timezone offset")
    predictions = {}
    for name, predictor in default_methods().items():
        predictions[name] = sorted(predictor(draws))
    rules = GAME_RULES[game]
    return {
        "experiment": "EXP-008 prospective prediction freeze",
        "game": game,
        "target_date": target_date,
        "frozen_at": frozen_at,
        "data_cutoff": draws[-1].draw_date.isoformat(),
        "last_draw_id": draws[-1].draw_id,
        "last_draw_numbers": list(draws[-1].numbers),
        "history_count": len(draws),
        "code_revision": code_revision,
        "number_count": rules["count"],
        "number_pool": rules["maximum"],
        "uniform_expected_hits": rules["count"] ** 2 / rules["maximum"],
        "predictions": predictions,
        "source_manifest": f"data/{game}_snapshot_2026-10-27.manifest.json",
        "status": "FROZEN_BEFORE_TARGET; shadow evaluation only; no method promoted",
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--superenalotto", required=True)
    parser.add_argument("--vincicasa", required=True)
    parser.add_argument("--frozen-at", required=True, help="ISO timestamp including timezone offset")
    parser.add_argument("--superenalotto-target", required=True, help="ISO date YYYY-MM-DD")
    parser.add_argument("--vincicasa-target", required=True, help="ISO date YYYY-MM-DD")
    parser.add_argument("--code-revision", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    se_draws = load_draws_csv(args.superenalotto, game="superenalotto")
    vc_draws = load_draws_csv(args.vincicasa, game="vincicasa")
    report = {
        "frozen_at": args.frozen_at,
        "code_revision": args.code_revision,
        "predictions": {
            "superenalotto": build_freeze(se_draws, args.superenalotto_target, args.frozen_at, args.code_revision),
            "vincicasa": build_freeze(vc_draws, args.vincicasa_target, args.frozen_at, args.code_revision),
        },
        "evaluation_policy": "Score every registered method after the target draw. Do not select or retune methods after seeing the outcome.",
    }
    serialized = json.dumps(report, indent=2, sort_keys=True)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
