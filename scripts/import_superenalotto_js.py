"""Convert the SuperEnalotto project's draws.js snapshot into AI Baby's canonical CSV."""
from __future__ import annotations

import argparse
import csv
import re
from datetime import datetime
from pathlib import Path

from ai_baby.lottery import Draw, validate_draw

ROW_RE = re.compile(
    r"\['(?P<date>\d{2}/\d{2}/\d{4})',\s*(?P<num>\d+),\s*"
    r"\[(?P<numbers>[\d,\s]+)\],\s*(?P<jolly>\d+)\]"
)


def parse_draws_js(source: str) -> list[Draw]:
    """Parse the documented SEED_DRAWS row format; ignore the Jolly for main-number scoring."""
    draws: list[Draw] = []
    for match in ROW_RE.finditer(source):
        parsed_date = datetime.strptime(match.group("date"), "%d/%m/%Y").date()
        contest_number = int(match.group("num"))
        numbers = tuple(int(token.strip()) for token in match.group("numbers").split(",") if token.strip())
        draw_id = f"superenalotto-{parsed_date.year}-{contest_number:03d}"
        draws.append(validate_draw(Draw(draw_id, "superenalotto", parsed_date, numbers)))

    if not draws:
        raise ValueError("no draw rows found; source format may have changed")
    if any(draws[i].draw_date > draws[i + 1].draw_date for i in range(len(draws) - 1)):
        raise ValueError("source draws are not chronological")
    if len({draw.draw_id for draw in draws}) != len(draws):
        raise ValueError("duplicate draw IDs found")
    return draws


def write_csv(draws: list[Draw], destination: str | Path) -> None:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["draw_id", "date", "game", "numbers"])
        for draw in draws:
            writer.writerow([
                draw.draw_id,
                draw.draw_date.isoformat(),
                draw.game,
                " ".join(map(str, draw.numbers)),
            ])


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="local copy of Superenalotto/src/data/draws.js")
    parser.add_argument("destination", help="destination canonical CSV path")
    args = parser.parse_args(argv)
    draws = parse_draws_js(Path(args.source).read_text(encoding="utf-8"))
    write_csv(draws, args.destination)
    print(f"Exported {len(draws)} draws; range {draws[0].draw_date}..{draws[-1].draw_date}")
    print("Note: Jolly and SuperStar are excluded; only six main numbers are exported.")


if __name__ == "__main__":
    main()
