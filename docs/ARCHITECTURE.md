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


## Ciclo di miglioramento continuo

`scripts/continuous_improvement.py` esegue una sweep riproducibile dei budget su tre benchmark sintetici. La scelta della configurazione è determinata esclusivamente dall'errore di sviluppo, con complessità e budget come spareggi; il test bloccato viene riportato solo dopo la selezione. Il benchmark quadratico agisce da sentinella di regressione.

Il workflow `.github/workflows/continuous-improvement.yml` esegue il ciclo giornalmente, su modifiche rilevanti e su richiesta manuale. Produce un riepilogo, artifacts e una cronologia persistente sotto `reports/`. La scrittura automatica è limitata ai report; il codice del motore non viene mai modificato né integrato automaticamente. Le modifiche algoritmiche richiedono una pull request revisionata.

**Limiti:** i benchmark sono sintetici, piccoli e non sostituiscono valutazioni su dati indipendenti reali. I workflow schedulati di GitHub possono essere ritardati o disattivati per inattività del repository pubblico; controllare periodicamente la scheda Actions. Vedi [documentazione GitHub sugli eventi pianificati](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).
