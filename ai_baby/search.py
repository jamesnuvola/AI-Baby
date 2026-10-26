"""Ricerca composizionale con budget e ordinamento per complessità."""
from dataclasses import dataclass
from itertools import combinations_with_replacement
from typing import Sequence
from .dsl import Expr, base_expressions

@dataclass(frozen=True)
class CandidateScore:
    expression: str
    complexity: int
    mae: float
    exact_accuracy: float
    n: int
    expression_obj: Expr

def _predict(expr: Expr, history: Sequence[float]) -> float | None:
    try:
        value = expr.evaluate(history)
        if value != value or abs(value) == float("inf"):
            return None
        return value
    except (ValueError, ArithmeticError, OverflowError):
        return None

def score_expr(expr: Expr, seq: Sequence[float], start: int, stop: int) -> CandidateScore | None:
    if start < 1 or stop > len(seq) or start >= stop:
        raise ValueError("Intervallo non valido.")
    errors, exact = [], 0
    for i in range(start, stop):
        pred = _predict(expr, seq[:i])
        if pred is None:
            return None
        err = pred - float(seq[i])
        errors.append(err)
        exact += abs(err) < 1e-9
    return CandidateScore(expr.render(), expr.complexity(),
                          sum(abs(e) for e in errors) / len(errors),
                          exact / len(errors), len(errors), expr)

def _ordered(exprs):
    return sorted(exprs.values(), key=lambda e: (e.complexity(), e.render()))

def generate_expressions(max_depth: int = 3, budget: int = 20000,
                         max_prev: int = 4, constants: range = range(-3, 4)) -> list[Expr]:
    """Genera espressioni a livelli e conserva prima quelle meno complesse."""
    if max_depth < 1 or budget < 1:
        raise ValueError("max_depth e budget devono essere positivi.")
    bases = base_expressions(max_prev=max_prev, constants=constants)
    all_exprs = {e.render(): e for e in bases}
    layer2 = {}
    if max_depth >= 2:
        for e in bases:
            for c in constants:
                for op in ("add_const", "mul_const"):
                    cand = Expr(op, (e, c))
                    layer2.setdefault(cand.render(), cand)
        for a, b in combinations_with_replacement(bases, 2):
            for op in ("add", "sub", "mul"):
                cand = Expr(op, (a, b))
                layer2.setdefault(cand.render(), cand)
        for e in _ordered(layer2):
            all_exprs.setdefault(e.render(), e)
    if max_depth >= 3:
        layer3 = {}
        for e in layer2.values():
            for b in bases:
                for op in ("add", "sub", "mul"):
                    for left, right in ((e, b), (b, e)):
                        cand = Expr(op, (left, right))
                        layer3.setdefault(cand.render(), cand)
        for e in _ordered(layer3):
            all_exprs.setdefault(e.render(), e)
    return _ordered(all_exprs)[:budget]

def search(seq: Sequence[float], train_end: int, max_depth: int = 3,
           budget: int = 20000) -> dict:
    if len(seq) < 5 or train_end < 3 or train_end >= len(seq):
        raise ValueError("Servono >=5 valori e 3 <= train_end < lunghezza sequenza.")
    expressions = generate_expressions(max_depth=max_depth, budget=budget)
    scored = []
    development_start = 5
    if train_end <= development_start:
        raise ValueError("train_end deve essere > 5 per confrontare tutte le primitive.")
    for expr in expressions:
        score = score_expr(expr, seq, development_start, train_end)
        if score is not None:
            scored.append(score)
    if not scored:
        raise RuntimeError("Nessuna espressione valutabile.")
    unique = {}
    for score in sorted(scored, key=lambda s: (s.mae, s.complexity, s.expression)):
        signature = []
        for i in range(development_start, train_end):
            pred = _predict(score.expression_obj, seq[:i])
            if pred is None:
                signature = None
                break
            signature.append(round(pred, 10))
        if signature is not None:
            unique.setdefault(tuple(signature), score)
    ranked = sorted(unique.values(), key=lambda s: (s.mae, s.complexity, s.expression))
    winner = ranked[0]
    test = score_expr(winner.expression_obj, seq, train_end, len(seq))
    baseline = score_expr(Expr("last"), seq, train_end, len(seq))
    return {
        "selected": winner.expression,
        "selected_complexity": winner.complexity,
        "development": {"mae": winner.mae, "exact_accuracy": winner.exact_accuracy, "n": winner.n},
        "test": None if test is None else {"mae": test.mae, "exact_accuracy": test.exact_accuracy, "n": test.n},
        "baseline_test": None if baseline is None else {"mae": baseline.mae, "exact_accuracy": baseline.exact_accuracy, "n": baseline.n},
        "candidate_count": len(expressions),
        "valid_candidate_count": len(scored),
        "unique_development_behaviors": len(unique),
        "budget": budget,
        "max_depth": max_depth,
        "top_candidates": [
            {"expression": s.expression, "complexity": s.complexity, "mae": s.mae,
             "exact_accuracy": s.exact_accuracy, "n": s.n}
            for s in ranked[:20]
        ],
    }
