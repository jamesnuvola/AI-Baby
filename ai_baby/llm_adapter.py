"""Contratto per un generatore LLM opzionale; nessuna rete o esecuzione dinamica."""
from typing import Protocol, Sequence

class HypothesisProvider(Protocol):
    def propose(self, problem_description: str, evidence: Sequence[float]) -> list[dict]:
        """Restituisce ipotesi strutturate e validate dal chiamante."""
        ...

class DisabledLLMProvider:
    def propose(self, problem_description: str, evidence: Sequence[float]) -> list[dict]:
        return []
