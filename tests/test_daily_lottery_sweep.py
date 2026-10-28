import unittest

from scripts.daily_lottery_sweep import parameter_grid


class DailyLotterySweepTests(unittest.TestCase):
    def test_parameter_grid_is_diverse_and_deterministic(self):
        first = parameter_grid("2026-10-28")
        second = parameter_grid("2026-10-28")
        next_day = parameter_grid("2026-10-29")
        self.assertEqual(list(first), list(second))
        self.assertNotEqual(
            {k for k in first if k.startswith("daily_")},
            {k for k in next_day if k.startswith("daily_")},
        )
        self.assertGreaterEqual(len(first), 25)
        self.assertIn("recent_frequency_window10", first)
        self.assertIn("recent_frequency_window80", first)
        self.assertIn("exponential_decay_tau40", first)
        self.assertIn("transition_overlap3_power3", first)
        self.assertIn("gap_neighbours40", first)
        self.assertIn("random_uniform_seed0", first)


if __name__ == "__main__":
    unittest.main()
