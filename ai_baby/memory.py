"""Memoria persistente SQLite."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

class MemoryStore:
    def __init__(self, db_path="ai_baby_memory.sqlite"):
        self.db_path = str(db_path)
        with self._connect() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_utc TEXT NOT NULL,
                problem TEXT NOT NULL,
                benchmark_version TEXT NOT NULL,
                selected_strategy TEXT NOT NULL,
                development_json TEXT NOT NULL,
                test_json TEXT NOT NULL,
                candidates_json TEXT NOT NULL,
                notes TEXT NOT NULL
            )""")
            con.execute("""CREATE TABLE IF NOT EXISTS strategies (
                name TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                complexity INTEGER NOT NULL,
                last_seen_utc TEXT NOT NULL,
                observations INTEGER NOT NULL DEFAULT 0
            )""")
    @contextmanager
    def _connect(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        try:
            with con:
                yield con
        finally:
            con.close()
    def save_experiment(self, *, problem, benchmark_version, selected_strategy,
                        development, test, candidates, notes=""):
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as con:
            cur = con.execute("""INSERT INTO experiments
                (created_utc, problem, benchmark_version, selected_strategy,
                 development_json, test_json, candidates_json, notes)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (now, problem, benchmark_version, selected_strategy,
                 json.dumps(development, sort_keys=True), json.dumps(test, sort_keys=True),
                 json.dumps(candidates, sort_keys=True), notes))
            for item in candidates:
                con.execute("""INSERT INTO strategies
                    (name, description, complexity, last_seen_utc, observations)
                    VALUES (?, ?, ?, ?, 1)
                    ON CONFLICT(name) DO UPDATE SET
                    description=excluded.description, complexity=excluded.complexity,
                    last_seen_utc=excluded.last_seen_utc,
                    observations=strategies.observations + 1""",
                    (item["name"], item["description"], item["complexity"], now))
            return int(cur.lastrowid)
    def history(self, limit=20):
        with self._connect() as con:
            rows = con.execute("SELECT * FROM experiments ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        out = []
        for row in rows:
            item = dict(row)
            for key in ("development_json", "test_json", "candidates_json"):
                item[key.removesuffix("_json")] = json.loads(item.pop(key))
            out.append(item)
        return out
