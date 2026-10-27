"""DSL sicuro per espressioni numeriche: nessuna eval/exec."""
from dataclasses import dataclass
from statistics import mean, median
from typing import Any, Sequence

@dataclass(frozen=True)
class Expr:
    op: str
    args: tuple[Any, ...] = ()

    def render(self) -> str:
        if self.op == "const":
            return str(self.args[0])
        if self.op == "prev":
            return f"prev({self.args[0]})"
        if self.op in {"last", "diff1", "diff2", "mean", "median", "sum_last2", "newton3"}:
            return self.op
        symbols = {"add": "+", "sub": "-", "mul": "*"}
        if self.op in symbols:
            return f"({self.args[0].render()} {symbols[self.op]} {self.args[1].render()})"
        if self.op == "add_const":
            return f"({self.args[0].render()} + {self.args[1]})"
        if self.op == "mul_const":
            return f"({self.args[0].render()} * {self.args[1]})"
        return f"{self.op}({', '.join(str(a) for a in self.args)})"

    def complexity(self) -> int:
        return 1 + sum(a.complexity() for a in self.args if isinstance(a, Expr))

    def evaluate(self, xs: Sequence[float]) -> float:
        if not xs:
            raise ValueError("Serve almeno un valore osservato.")
        if self.op == "const":
            return float(self.args[0])
        if self.op == "last":
            return float(xs[-1])
        if self.op == "prev":
            k = int(self.args[0])
            if k < 1 or len(xs) < k + 1:
                raise ValueError("Storia insufficiente per prev(k).")
            return float(xs[-1-k])
        if self.op == "diff1":
            if len(xs) < 2:
                raise ValueError("Storia insufficiente per diff1.")
            return float(xs[-1] - xs[-2])
        if self.op == "diff2":
            if len(xs) < 3:
                raise ValueError("Storia insufficiente per diff2.")
            return float(xs[-1] - 2 * xs[-2] + xs[-3])
        if self.op == "newton3":
            if len(xs) < 4:
                raise ValueError("Storia insufficiente per newton3.")
            a, b, c, d = map(float, xs[-4:])
            first = d - c
            second = d - 2 * c + b
            third = d - 3 * c + 3 * b - a
            return float(d + first + second + third)
        if self.op == "mean":
            return float(mean(xs))
        if self.op == "median":
            return float(median(xs))
        if self.op == "sum_last2":
            if len(xs) < 2:
                raise ValueError("Storia insufficiente per sum_last2.")
            return float(xs[-1] + xs[-2])
        a = self.args[0].evaluate(xs)
        if self.op == "add_const":
            return float(a + self.args[1])
        if self.op == "mul_const":
            return float(a * self.args[1])
        b = self.args[1].evaluate(xs)
        if self.op == "add":
            return float(a + b)
        if self.op == "sub":
            return float(a - b)
        if self.op == "mul":
            return float(a * b)
        raise ValueError(f"Operatore non supportato: {self.op}")

def base_expressions(max_prev: int = 4, constants: range = range(-3, 4)) -> list[Expr]:
    exprs = [Expr(op) for op in ("last", "diff1", "diff2", "mean", "median", "sum_last2", "newton3")]
    exprs += [Expr("prev", (k,)) for k in range(1, max_prev + 1)]
    exprs += [Expr("const", (c,)) for c in constants]
    return exprs
