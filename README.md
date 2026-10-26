# AI Baby Lab

**Prototipo di ricerca cognitiva sperimentale.** AI Baby 0.2 esplora espressioni matematiche composizionali in un DSL esplicito, misura le prestazioni rispetto a una baseline e registra gli esperimenti in SQLite.

> **Stato scientifico:** proof of concept. I risultati attuali sono limitati a una sequenza sintetica; non dimostrano intelligenza generale o capacità predittive su dati reali.

## Avvio rapido

Richiede Python 3.10 o successivo, senza dipendenze esterne.

```bash
python -m unittest discover -s tests -v
python -m ai_baby.cli demo --db ai_baby_memory.sqlite
python -m ai_baby.cli history --db ai_baby_memory.sqlite
```

## GitHub Codespaces

Apri **Code → Codespaces → Create codespace on main**. Nel terminale esegui i test e poi la demo. La configurazione `.devcontainer/devcontainer.json` prepara un ambiente Python.

## Integrazione continua

Il workflow `.github/workflows/ci.yml` esegue test e smoke test con Python 3.10–3.13 su push, pull request e avvio manuale. Verificare lo stato reale nella scheda **Actions**: la presenza del file non garantisce che ogni esecuzione sia passata.

## Registro degli esperimenti

- `RESULTS_LOG.md`: risultati storici e modello per gli esperimenti successivi.
- `experiments/README.md`: campi metodologici da registrare.
- `docs/ARCHITECTURE.md`: architettura e limiti.

Ogni prova dovrebbe riportare commit, dati, split, budget, baseline, metriche, risorse, esito e limiti. Non selezionare candidati in base al test finale.

## Limiti tecnici

- Spazio di ricerca circoscritto al DSL nel codice.
- Nessun LLM collegato nella v0.2.
- La memoria SQLite è locale, salvo esportazione esplicita; codice e registro Markdown sono versionabili.
- Non inserire chiavi API, password, dati personali o segreti in un repository pubblico.

## Licenza

Non è stata ancora scelta una licenza open source. Vedi `LICENSE_DECISION.md` prima di autorizzare formalmente il riuso.
