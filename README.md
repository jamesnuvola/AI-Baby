# AI Baby Lab

**Prototipo di ricerca cognitiva sperimentale.** AI Baby 0.2 esplora espressioni matematiche composizionali in un DSL esplicito, misura le prestazioni rispetto a una baseline e registra gli esperimenti in SQLite.

> **Stato scientifico:** proof of concept. I benchmark matematici sintetici sono separati dal nuovo laboratorio esplorativo sulle estrazioni reali. Nessun vantaggio predittivo sulle lotterie è stato dimostrato.

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

## Miglioramento continuo automatico

Il workflow **Continuous Improvement Lab** esegue unit test e una ricerca riproducibile su tre benchmark sintetici (lineare, quadratico, Fibonacci), confrontando budget di 1.000, 5.000 e 20.000 candidati. Viene eseguito ogni giorno alle 05:37 UTC, quando si modificano codice/test rilevanti e manualmente da [GitHub Actions](https://github.com/jamesnuvola/AI-Baby/actions/workflows/continuous-improvement.yml).

- Sceglie il budget usando solo le metriche di sviluppo del seed 0; i semi 1 e 2 sono controlli di robustezza a budget congelato e nessuna metrica di test determina la selezione.
- Riporta MAE medio e peggiore tra i semi, accuratezza esatta media, baseline e dettagli per seed; il caso cubico è diagnostico e può evidenziare limiti del DSL.
- Pubblica un riepilogo nel job e carica JSON/Markdown come artifact per 90 giorni.
- Salva anche report e storico append-only in `reports/` tramite un commit del bot, se le policy del repository consentono il push.
- Fallisce sul benchmark quadratico se la regressione sentinella non mantiene MAE 0 e accuratezza esatta 100%.
- Non modifica automaticamente il motore e non fa merge: le modifiche algoritmiche richiedono revisione umana.

Il workflow è stato aggiunto e il suo file è stato verificato nella repository. L'esecuzione remota va considerata confermata solo dopo aver controllato lo stato del job nella scheda Actions.

## Registro degli esperimenti

- `RESULTS_LOG.md`: risultati storici e modello per gli esperimenti successivi.
- `experiments/README.md`: campi metodologici da registrare.
- `docs/ARCHITECTURE.md`: architettura e limiti.

Ogni prova dovrebbe riportare commit, dati, split, budget, baseline, metriche, risorse, esito e limiti. Non selezionare candidati in base al test finale.

## Laboratorio sperimentale SuperEnalotto / VinciCasa

AI Baby include ora un laboratorio distinto per testare eventuali segnali predittivi nelle estrazioni reali. I due giochi sono valutati separatamente; ogni metodo usa soltanto estrazioni precedenti al target.

- Dati canonici e manifesti di provenienza: `data/superenalotto_snapshot_2026-10-27.csv`, `data/vincicasa_snapshot_2026-10-27.csv` e i corrispondenti `.manifest.json`.
- Protocollo e limiti: `docs/LOTTERY_RESEARCH_PROTOCOL.md`.
- Metodi iniziali e risultati: `reports/LOTTERY_EXP008_INITIAL_BACKTEST_2026-10-28.md`.
- Analogie di transizione e gap: `reports/LOTTERY_EXP009_STRUCTURAL_ANALOGUES_2026-10-28.md`.
- Registro persistente: `RESULTS_LOG.md`.
- Validazione dati, scoring, baseline e walk-forward: `ai_baby/lottery.py`.
- Metodi sperimentali: `ai_baby/lottery_methods.py`.
- Runner benchmark: `scripts/lottery_benchmark.py`.
- Freeze prospettico: `reports/PREDICTION_FREEZE_2026-10-28.md` e il corrispondente JSON.

Esempio di benchmark:

```bash
python -m scripts.lottery_benchmark data/vincicasa_snapshot_2026-10-27.csv --game vincicasa --minimum-history 100 --simulations 500 --output reports/exp008-vincicasa.json
```

Il freeze prospettico conserva le previsioni di tutti i metodi prima delle estrazioni successive; il workflow CI verifica che il file generato coincida con il record congelato.

**Importante:** le finestre storiche 2023–2024 e 2025+ sono già state esplorate in precedenti ricerche SONAR e non sono un test cieco nuovo. I risultati sono esplorativi, instabili e non provano un vantaggio; nessun metodo viene promosso in base a un singolo periodo o a una coincidenza.

- Automazione giornaliera: workflow [Daily Lottery Research](.github/workflows/daily-lottery-research.yml), eseguito ogni giorno alle 04:17 UTC e attivabile manualmente da GitHub Actions.
- Sweep di variabili: [scripts/daily_lottery_sweep.py](scripts/daily_lottery_sweep.py), con report datati in [reports/continuous/](reports/continuous/) e artefatti GitHub Actions conservati per 90 giorni.
- La classifica automatica è solo esplorativa: non modifica né promuove automaticamente il metodo predefinito. I dataset sono ancora snapshot fissi; l'aggiornamento automatico dai bollettini ufficiali è un passaggio separato da implementare e verificare.

## Limiti tecnici

- Spazio di ricerca circoscritto al DSL nel codice; il candidato newton3 applica l'estrapolazione alle differenze finite fino al terzo ordine e va valutato contro le altre famiglie, non assunto come sempre corretto.
- Nessun LLM collegato nella v0.2.
- La memoria SQLite è locale, salvo esportazione esplicita; codice e registro Markdown sono versionabili.
- Non inserire chiavi API, password, dati personali o segreti in un repository pubblico.

## Licenza

Non è stata ancora scelta una licenza open source. Vedi `LICENSE_DECISION.md` prima di autorizzare formalmente il riuso.
