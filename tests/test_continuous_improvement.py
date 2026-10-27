import unittest
from scripts.continuous_improvement import SEEDS, benchmark_cases, _metric_summary

class ContinuousImprovementTests(unittest.TestCase):
    def test_benchmark_families_are_stable_and_cover_new_patterns(self):
        first = benchmark_cases(0)
        self.assertEqual(first, benchmark_cases(0))
        self.assertEqual(set(first), {"linear", "quadratic", "fibonacci", "geometric", "cubic_diagnostic"})

    def test_seeds_change_cases_deterministically(self):
        self.assertNotEqual(benchmark_cases(0)["linear"], benchmark_cases(1)["linear"])
        self.assertNotEqual(benchmark_cases(0)["quadratic"], benchmark_cases(2)["quadratic"])
        self.assertEqual(benchmark_cases(1), benchmark_cases(1))
        self.assertEqual(SEEDS, (0, 1, 2))

    def test_metric_summary_reports_mean_worst_and_count(self):
        self.assertEqual(_metric_summary([{"mae": 0.0}, {"mae": 2.0}, {"mae": 1.0}], "mae"),
                         {"mean": 1.0, "worst": 2.0, "n": 3})

    def test_metric_summary_handles_empty_metrics(self):
        self.assertEqual(_metric_summary([{"mae": None}], "mae"),
                         {"mean": None, "worst": None, "n": 0})

if __name__ == "__main__":
    unittest.main()
