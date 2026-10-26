"""Orchestratore del ciclo di ricerca."""
from .search import search
from .memory import MemoryStore

class AIBaby:
    def __init__(self, memory: MemoryStore):
        self.memory = memory

    def investigate_sequence(self, sequence, train_end, problem="synthetic_sequence_rule_discovery",
                            benchmark_version="synthetic-v2", max_depth=3, budget=20000):
        result = search(sequence, train_end, max_depth=max_depth, budget=budget)
        candidates = [
            {"name": item["expression"], "description": "Espressione DSL generata",
             "complexity": item["complexity"]}
            for item in result["top_candidates"]
        ]
        exp_id = self.memory.save_experiment(
            problem=problem, benchmark_version=benchmark_version,
            selected_strategy=result["selected"], development=result["development"],
            test=result["test"] or {}, candidates=candidates,
            notes=f"DSL composizionale v0.2; budget={budget}; depth={max_depth}; test non usato per selezionare."
        )
        result["experiment_id"] = exp_id
        result["problem"] = problem
        result["benchmark_version"] = benchmark_version
        return result
