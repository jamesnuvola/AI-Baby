import tempfile
import unittest
from datetime import date
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
