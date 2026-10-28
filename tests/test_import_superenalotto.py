import tempfile
import unittest
from datetime import date
from pathlib import Path

from ai_baby.lottery import load_draws_csv
from scripts.import_superenalotto_js import parse_draws_js, write_csv


class SuperEnalottoImportTests(unittest.TestCase):
    def test_parse_and_convert_main_numbers(self):
        source = """
        const SEED_DRAWS = [
          ['02/01/2009', 1, [16, 19, 29, 34, 48, 64], 53],
          ['03/01/2009', 2, [17, 24, 25, 40, 58, 64], 27]
        ]
        """
        draws = parse_draws_js(source)
        self.assertEqual(len(draws), 2)
        self.assertEqual(draws[0].draw_date, date(2009, 1, 2))
        self.assertEqual(draws[0].numbers, (16, 19, 29, 34, 48, 64))
        self.assertEqual(draws[1].draw_id, "superenalotto-2009-002")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "superenalotto.csv"
            write_csv(draws, path)
            loaded = load_draws_csv(path, game="superenalotto")
            self.assertEqual(loaded, draws)

    def test_reject_changed_or_invalid_source(self):
        with self.assertRaisesRegex(ValueError, "no draw rows"):
            parse_draws_js("const SEED_DRAWS = [];")
        with self.assertRaises(ValueError):
            parse_draws_js("['02/01/2009', 1, [1, 1, 2, 3, 4, 5], 53]")


if __name__ == "__main__":
    unittest.main()
