import unittest
from datetime import date

from ai_baby.lottery import Draw, GAME_RULES
from ai_baby.lottery_methods import (
    anti_hot,
    exponential_decay,
    global_frequency,
    overdue_first,
    random_uniform,
    recent_frequency,
    transition_analogue,
    gap_trajectory_neighbours,
)


class LotteryMethodTests(unittest.TestCase):
    def setUp(self):
        self.history = [
            Draw(str(i), "vincicasa", date(2026, 1, i + 1), (1, 2, 3, 4, 5))
            for i in range(10)
        ]

    def test_each_method_returns_valid_distinct_ticket(self):
        methods = [
            global_frequency,
            recent_frequency(5),
            anti_hot(5),
            exponential_decay(3),
            overdue_first,
            random_uniform(7),
            transition_analogue(min_overlap=2, power=3),
            gap_trajectory_neighbours(neighbours=5),
        ]
        for method in methods:
            prediction = method(self.history)
            self.assertEqual(len(prediction), GAME_RULES["vincicasa"]["count"])
            self.assertEqual(len(set(prediction)), 5)
            self.assertTrue(all(1 <= n <= 40 for n in prediction))

    def test_random_stream_is_reproducible(self):
        a = random_uniform(123)
        b = random_uniform(123)
        self.assertEqual(a(self.history), b(self.history))
        self.assertEqual(a(self.history), b(self.history))

    def test_anti_hot_prefers_numbers_absent_from_recent_window(self):
        prediction = anti_hot(10)(self.history)
        self.assertTrue(all(n not in {1, 2, 3, 4, 5} for n in prediction))


if __name__ == "__main__":
    unittest.main()
