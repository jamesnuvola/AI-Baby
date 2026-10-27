import tempfile
import unittest
from pathlib import Path
from ai_baby.dsl import Expr
from ai_baby.search import generate_expressions, search
from ai_baby.core import AIBaby
from ai_baby.memory import MemoryStore
from ai_baby.cli import demo_sequence

class DSLTests(unittest.TestCase):
    def test_second_difference_expression(self):
        expr = Expr("add", (
            Expr("last"),
            Expr("add", (Expr("diff1"), Expr("diff1")))
        ))
        self.assertAlmostEqual(expr.evaluate([1, 4, 9]), 19.0)

    def test_invalid_history_rejected(self):
        with self.assertRaises(ValueError):
            Expr("diff2").evaluate([1, 2])

    def test_newton3_extrapolates_cubic_sequences(self):
        expr = Expr("newton3")
        for seed in (0, 1, 2):
            seq = [n ** 3 + seed for n in range(8)]
            self.assertEqual(expr.evaluate(seq[:7]), seq[7])
        with self.assertRaises(ValueError):
            expr.evaluate([1, 8, 27])

    def test_generation_is_bounded_and_deterministic(self):
        a = [x.render() for x in generate_expressions(max_depth=2, budget=180)]
        b = [x.render() for x in generate_expressions(max_depth=2, budget=180)]
        self.assertEqual(a, b)
        self.assertLessEqual(len(a), 180)

    def test_search_generalizes_on_synthetic_quadratic(self):
        seq = demo_sequence()
        result = search(seq, train_end=8, max_depth=3, budget=20000)
        self.assertEqual(result["test"]["n"], 4)
        self.assertEqual(result["test"]["mae"], 0.0)
        self.assertEqual(result["test"]["exact_accuracy"], 1.0)
        self.assertIn("baseline_test", result)

    def test_search_finds_newton3_for_cubic_diagnostic(self):
        seq = [n ** 3 for n in range(12)]
        result = search(seq, train_end=8, max_depth=3, budget=1000)
        self.assertEqual(result["test"]["mae"], 0.0)
        self.assertEqual(result["test"]["exact_accuracy"], 1.0)
        self.assertEqual(result["selected"], "newton3")

    def test_memory_persists_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "memory.sqlite"
            baby = AIBaby(MemoryStore(db))
            result = baby.investigate_sequence(demo_sequence(), train_end=8, budget=500)
            history = MemoryStore(db).history()
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["selected_strategy"], result["selected"])

if __name__ == "__main__":
    unittest.main()
