import json
import unittest
from datetime import date
from pathlib import Path

from ai_baby.lottery import Draw, load_draws_csv
from scripts.freeze_lottery_predictions import build_freeze


class PredictionFreezeTests(unittest.TestCase):
    def setUp(self):
        self.draws = [
            Draw(str(i), "vincicasa", date(2026, 10, i + 1), (1 + i, 8 + i, 15 + i, 22 + i, 30 + i))
            for i in range(5)
        ]

    def test_freeze_records_all_methods_and_strict_future_target(self):
        result = build_freeze(
            self.draws,
            target_date="2026-10-29",
            frozen_at="2026-10-28T11:06:13+01:00",
            code_revision="test-revision",
        )
        self.assertEqual(result["data_cutoff"], "2026-10-05")
        self.assertEqual(result["last_draw_id"], "4")
        self.assertIn("gap_trajectory_nearest20", result["predictions"])
        self.assertIn("transition_analogue_overlap2_power3", result["predictions"])
        self.assertIn("random_uniform_seed0", result["predictions"])
        self.assertIn("FROZEN_BEFORE_TARGET", result["status"])

    def test_freeze_rejects_target_not_after_data_and_naive_timestamp(self):
        with self.assertRaisesRegex(ValueError, "later than"):
            build_freeze(self.draws, "2026-10-05", "2026-10-28T11:06:13+01:00", "x")
        with self.assertRaisesRegex(ValueError, "timezone"):
            build_freeze(self.draws, "2026-10-29", "2026-10-28T11:06:13", "x")

    def test_committed_freeze_matches_generated_predictions(self):
        root = Path(__file__).resolve().parents[1]
        record = json.loads((root / "reports" / "prediction-freeze-2026-10-28.json").read_text(encoding="utf-8"))
        for game, target in (("superenalotto", "2026-10-29"), ("vincicasa", "2026-10-28")):
            draws = load_draws_csv(root / "data" / f"{game}_snapshot_2026-10-27.csv", game=game)
            generated = build_freeze(
                draws,
                target_date=target,
                frozen_at=record["frozen_at"],
                code_revision=record["code_revision"],
            )
            self.assertEqual(generated, record["predictions"][game])


if __name__ == "__main__":
    unittest.main()
