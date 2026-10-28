import tempfile
import json
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from scripts.daily_lottery_sweep import build_exact_rule_catalog, write_prospective_freezes

from ai_baby.lottery import (
    Draw,
    load_draws_csv,
    rolling_origin_backtest,
    score_prediction,
    simulate_uniform_baseline,
    uniform_expected_hits,
    validate_draw,
)


class LotteryDataTests(unittest.TestCase):
    def test_validate_superenalotto_and_sort_numbers(self):
        draw = validate_draw(Draw("s1", "SuperEnalotto", date(2026, 1, 1), (90, 2, 4, 6, 8, 10)))
        self.assertEqual(draw.game, "superenalotto")
        self.assertEqual(draw.numbers, (2, 4, 6, 8, 10, 90))

    def test_rejects_wrong_cardinality_duplicate_and_out_of_range(self):
        with self.assertRaises(ValueError):
            validate_draw(Draw("x", "vincicasa", date(2026, 1, 1), (1, 2, 3, 4)))
        with self.assertRaises(ValueError):
            validate_draw(Draw("x", "superenalotto", date(2026, 1, 1), (1, 1, 2, 3, 4, 5)))
        with self.assertRaises(ValueError):
            validate_draw(Draw("x", "vincicasa", date(2026, 1, 1), (1, 2, 3, 4, 41)))

    def test_csv_loader_checks_schema_and_chronology(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "draws.csv"
            path.write_text(
                "draw_id,date,game,numbers\n"
                "a,2026-01-01,vincicasa,1 2 3 4 5\n"
                "b,2026-01-02,vincicasa,2 4 6 8 10\n",
                encoding="utf-8",
            )
            draws = load_draws_csv(path, game="vincicasa")
            self.assertEqual(len(draws), 2)
            self.assertEqual(draws[0].numbers, (1, 2, 3, 4, 5))
            path.write_text(
                "draw_id,date,game,numbers\n"
                "b,2026-01-02,vincicasa,2 4 6 8 10\n"
                "a,2026-01-01,vincicasa,1 2 3 4 5\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "chronologically"):
                load_draws_csv(path)

    def test_exact_hit_scoring_and_uniform_expectation(self):
        self.assertEqual(score_prediction((1, 2, 3, 4, 5), (1, 3, 5, 7, 9), 5, 1, 40), 3)
        self.assertAlmostEqual(uniform_expected_hits(5, 40), 0.625)
        with self.assertRaises(ValueError):
            score_prediction((1, 1, 2, 3, 4), (1, 3, 5, 7, 9), 5, 1, 40)

    def test_random_baseline_is_reproducible(self):
        actual = [(1, 2, 3, 4, 5), (6, 7, 8, 9, 10)]
        a = simulate_uniform_baseline(actual, 5, 40, simulations=100, seed=42)
        b = simulate_uniform_baseline(actual, 5, 40, simulations=100, seed=42)
        self.assertEqual(a, b)
        self.assertEqual(a["theoretical_mean_hits"], 0.625)

    def test_rolling_backtest_never_exposes_target_draw(self):
        draws = [
            Draw(str(i), "vincicasa", date(2026, 1, i + 1), (1, 2, 3, 4, 5))
            for i in range(5)
        ]
        history_sizes = []

        def predictor(history):
            history_sizes.append(len(history))
            self.assertNotIn("4", [d.draw_id for d in history])
            return (1, 2, 3, 4, 5)

        report = rolling_origin_backtest(draws, predictor, minimum_history=3)
        self.assertEqual(report["evaluated_draws"], 2)
        self.assertEqual(history_sizes, [3, 4])
        self.assertEqual(report["mean_hits"], 5.0)
        self.assertEqual(report["theoretical_uniform_mean_hits"], 0.625)

    def test_pinned_superenalotto_snapshot_is_valid_and_stale_as_documented(self):
        root = Path(__file__).resolve().parents[1]
        draws = load_draws_csv(root / "data" / "superenalotto_snapshot_2026-10-10.csv", game="superenalotto")
        self.assertEqual(len(draws), 2934)
        self.assertEqual(draws[0].draw_date, date(2009, 1, 2))
        self.assertEqual(draws[-1].draw_date, date(2026, 10, 10))
        self.assertTrue(all(len(d.numbers) == 6 and len(set(d.numbers)) == 6 for d in draws))

    def test_pinned_vincicasa_snapshot_is_valid_and_current(self):
        root = Path(__file__).resolve().parents[1]
        draws = load_draws_csv(root / "data" / "vincicasa_snapshot_2026-10-27.csv", game="vincicasa")
        self.assertEqual(len(draws), 3390)
        self.assertEqual(draws[0].draw_date, date(2017, 7, 17))
        self.assertEqual(draws[-1].draw_date, date(2026, 10, 27))
        self.assertEqual(draws[-1].numbers, (1, 6, 8, 28, 34))
        self.assertTrue(all(len(d.numbers) == 5 and len(set(d.numbers)) == 5 for d in draws))

    def test_updated_superenalotto_snapshot_matches_official_latest_draw(self):
        root = Path(__file__).resolve().parents[1]
        draws = load_draws_csv(root / "data" / "superenalotto_snapshot_2026-10-27.csv", game="superenalotto")
        self.assertEqual(len(draws), 2943)
        self.assertEqual(draws[0].draw_date, date(2009, 1, 2))
        self.assertEqual(draws[-1].draw_date, date(2026, 10, 27))
        self.assertEqual(draws[-1].numbers, (23, 34, 44, 48, 64, 70))
        self.assertTrue(all(len(d.numbers) == 6 and len(set(d.numbers)) == 6 for d in draws))




    def test_exact_rule_catalog_keeps_full_ticket_and_rank_matches_independently(self):
        records = {
            "poor_average_but_exact_once": [
                {
                    "target_draw_id": "d1",
                    "target_date": "2025-01-01",
                    "history_size": 100,
                    "prediction": [1, 2, 3, 4, 5],
                    "actual": [1, 2, 3, 4, 5],
                    "hits": 5,
                },
                {
                    "target_draw_id": "d2",
                    "target_date": "2025-01-02",
                    "history_size": 101,
                    "prediction": [10, 11, 12, 13, 14],
                    "actual": [1, 2, 3, 4, 5],
                    "hits": 0,
                },
            ],
            "rank_one_only": [
                {
                    "target_draw_id": "d1",
                    "target_date": "2025-01-01",
                    "history_size": 100,
                    "prediction": [1, 8, 9, 10, 11],
                    "actual": [1, 2, 3, 4, 5],
                    "hits": 1,
                },
            ],
        }
        catalog = build_exact_rule_catalog(
            "vincicasa", records, "2026-10-28", "fixture.csv", "a" * 64
        )
        self.assertEqual(catalog["rule_count_evaluated"], 2)
        self.assertEqual(len(catalog["full_position_exact_matches"]), 1)
        exact = catalog["full_position_exact_matches"][0]
        self.assertEqual(exact["method"], "poor_average_but_exact_once")
        self.assertEqual(exact["target_draw_id"], "d1")
        self.assertEqual(len(catalog["rank_exact_matches"]), 6)
        rank_one = [item for item in catalog["rank_exact_matches"] if item["rank"] == 1]
        self.assertEqual(len(rank_one), 2)
        self.assertTrue(all(item["predicted_number"] == item["actual_number"] == 1 for item in rank_one))
        self.assertTrue(all(item["full_ticket_also_exact"] for item in catalog["rank_exact_matches"] if item["method"] == "poor_average_but_exact_once" and item["target_draw_id"] == "d1"))
        self.assertEqual(catalog["dataset_sha256"], "a" * 64)
        self.assertEqual(catalog["rank_summary"][0]["exact_match_count"], 2)

    def test_prospective_freeze_records_predictions_and_dataset_hashes(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            outdir = Path(tmp)
            write_prospective_freezes(
                datetime(2026, 10, 28, 18, 0, tzinfo=timezone.utc), outdir
            )
            for game, count, maximum, expected_latest in (
                ("vincicasa", 5, 40, "2026-10-27"),
                ("superenalotto", 6, 90, "2026-10-27"),
            ):
                path = outdir / f"prospective-{game}-latest.json"
                record = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(record["record_type"], "prospective_prediction_freeze")
                self.assertEqual(record["history"]["latest_draw_date"], expected_latest)
                self.assertEqual(len(record["history"]["sha256"]), 64)
                self.assertEqual(record["history"]["sha256"], __import__("hashlib").sha256(
                    (root / record["history"]["dataset_path"]).read_bytes()
                ).hexdigest())
                self.assertIsNone(record["target"]["draw_date"])
                self.assertEqual(record["evaluation_status"], "pending; score only after the target draw is published")
                self.assertEqual(len(record["predictions"]), 3)
                for prediction in record["predictions"].values():
                    self.assertEqual(len(prediction), count)
                    self.assertEqual(prediction, sorted(set(prediction)))
                    self.assertTrue(all(1 <= n <= maximum for n in prediction))
                dated = list(outdir.glob(f"prospective-{game}-20261028T180000Z.json"))
                self.assertEqual(len(dated), 1)


if __name__ == "__main__":
    unittest.main()
