import unittest
from datetime import date, timedelta

from ai_baby.lottery import Draw, GAME_RULES
from ai_baby.trajectory_decoder import chronological_trajectory_decoder


class ChronologicalTrajectoryDecoderTests(unittest.TestCase):
    def setUp(self):
        patterns = [
            (2, 8, 15, 27, 36), (3, 9, 16, 28, 37), (1, 7, 14, 26, 35),
            (4, 10, 17, 29, 38), (2, 9, 15, 28, 36), (5, 11, 18, 30, 39),
            (1, 8, 16, 27, 34), (3, 10, 19, 29, 40), (2, 7, 17, 26, 37),
            (4, 12, 18, 31, 39), (1, 9, 14, 30, 38), (5, 8, 20, 28, 35),
            (2, 10, 16, 29, 37), (4, 9, 18, 27, 39), (1, 11, 17, 30, 36),
        ]
        self.history = [
            Draw(str(i), "vincicasa", date(2026, 1, 1) + timedelta(days=i), numbers)
            for i, numbers in enumerate(patterns)
        ]

    def test_prediction_is_valid_sorted_and_reproducible(self):
        predictor = chronological_trajectory_decoder(window=4, neighbours=5, recency_tau=20)
        first = predictor(self.history)
        self.assertEqual(first, predictor(self.history))
        self.assertEqual(len(first), GAME_RULES["vincicasa"]["count"])
        self.assertEqual(tuple(sorted(set(first))), first)
        self.assertTrue(all(1 <= n <= 40 for n in first))

    def test_requires_sufficient_history(self):
        with self.assertRaises(ValueError):
            chronological_trajectory_decoder(window=5)(self.history[:5])

    def test_parameters_are_validated(self):
        for kwargs in ({"window": 1}, {"neighbours": 0}, {"recency_tau": 0}):
            with self.assertRaises(ValueError):
                chronological_trajectory_decoder(**kwargs)


if __name__ == "__main__":
    unittest.main()
