# Architettura — AI Baby 0.2

## Componenti

- `ai_baby/dsl.py`: rappresentazione e valutazione delle espressioni candidate.
- `ai_baby/search.py`: generazione e ricerca limitata nello spazio definito dal DSL.
- `ai_baby/core.py`: coordinamento dell'indagine e selezione.
- `ai_baby/memory.py`: persistenza dei risultati in SQLite.
- `ai_baby/llm_adapter.py`: interfaccia predisposta per una futura integrazione; non implica che un LLM sia già collegato.
- `ai_baby/cli.py`: comandi demo e consultazione della memoria.
- `tests/`: test automatici.
- `experiments/` e `RESULTS_LOG.md`: metodologia e registro degli esperimenti.

## Limiti correnti

La ricerca è limitata agli operatori e alle costanti definiti nel codice. Non esegue codice arbitrario generato da un modello e non include ancora un LLM. Le metriche attuali derivano da una demo sintetica con un set di test molto piccolo. Qualsiasi affermazione più ampia richiede benchmark indipendenti, più seed, baseline adeguate e test bloccati.
