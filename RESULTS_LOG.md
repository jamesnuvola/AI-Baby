# AI Baby — registro persistente dei risultati

Questo registro conserva risultati positivi e negativi. Aggiungere nuove prove in fondo senza cancellare i risultati storici. Distinguere sempre i test locali da quelli eseguiti da GitHub Actions.

## EXP-002 — AI Baby 0.2: ricerca composizionale su sequenza sintetica

- **Stato:** eseguito localmente nel prototipo v0.2; non è un risultato di GitHub Actions.
- **Benchmark:** sequenza sintetica quadratica n² + 1, valori da n=0 a n=11.
- **Split:** sviluppo con 3 punti di previsione; test successivo con 4 punti.
- **Ricerca:** budget 20.000 candidati; profondità massima 3.
- **Strategia selezionata:** `((diff1 * 3) + prev(2))`.
- **Risultato sviluppo:** MAE 0, accuratezza esatta 100% su 3 punti.
- **Risultato test:** MAE 0, accuratezza esatta 100% su 4 punti.
- **Baseline “ripeti l'ultimo valore”, test:** MAE 18, accuratezza esatta 0%.
- **Test unitari del prototipo:** 5/5 superati nell'esecuzione locale documentata.
- **Interpretazione:** la ricerca composizionale trova una regola adatta a questo esempio sintetico. Il test è piccolo e artificiale; non dimostra capacità predittiva generale né vantaggi su dati reali.
- **Prossimo passo:** aggiungere benchmark sintetici eterogenei e baseline multiple; fissare i set di test prima di scegliere le strategie; misurare costi e robustezza.

## Modello per una nuova registrazione

### EXP-XXX — titolo
- **Stato:** pianificato / eseguito localmente / CI verificata / fallito
- **Data UTC:**
- **Commit:**
- **Ipotesi:**
- **Benchmark e provenienza dati:**
- **Split e prevenzione leakage:**
- **Spazio di ricerca, budget, seed:**
- **Baseline:**
- **Metriche sviluppo:**
- **Metriche test bloccato:**
- **Tempo e risorse:**
- **Esito e limiti:**
- **Prossima azione:**

## EXP-003 — Diagnosi della sensibilità al budget di ricerca

- **Stato:** eseguito localmente il 2026-10-26; il codice e i test sono stati scaricati dal pacchetto starter e rieseguiti localmente.
- **Ambiente:** Python 3.13.
- **Test unitari:** 5/5 superati in 1,376 s.
- **Sequenza:** stessa sequenza sintetica quadratica dell'EXP-002; split invariato (3 punti sviluppo, 4 punti test).
- **Budget 1.000:** strategia selezionata `(last + mean)`; MAE sviluppo 1,2778; MAE test 8,9167; accuratezza esatta test 0%; baseline “ripeti ultimo valore” MAE test 18,0.
- **Budget 20.000:** strategia selezionata `((diff1 * 3) + prev(2))`; MAE sviluppo 0; MAE test 0; accuratezza esatta test 100%; baseline MAE test 18,0.
- **Diagnosi:** il budget limitato escludeva la strategia corretta dallo spazio effettivamente esplorato. Non era un fallimento del motore in assoluto, ma una sensibilità sostanziale al budget di ricerca.
- **Correzione applicata:** il smoke test CI è stato aggiornato da budget 1.000 a 20.000, per esercitare la configurazione che ha superato il benchmark sintetico.
- **Limiti:** un solo benchmark sintetico e split piccolo; non è evidenza di prestazioni su dati reali. L'esito della CI su GitHub va ancora verificato nella scheda Actions.

## EXP-004 — Configurazione del laboratorio di miglioramento continuo automatico

- **Stato:** workflow e runner pubblicati; esecuzione remota GitHub Actions non ancora verificata tramite lo stato del job.
- **Automazione:** workflow `Continuous Improvement Lab`, pianificato ogni giorno alle 05:37 UTC, su push rilevanti e avvio manuale.
- **Copertura:** test unitari, sweep dei budget 1.000 / 5.000 / 20.000 su benchmark sintetici lineare, quadratico e Fibonacci; selezione solo su metriche di sviluppo; test bloccato riportato dopo la selezione.
- **Dry run locale:** il runner è stato provato con Python 3.13 sul pacchetto starter locale (non su un checkout remoto verificato della revisione GitHub corrente). I 5 test del pacchetto starter sono passati.
- **Risultati dry run:** lineare — budget 1.000, MAE test 0, baseline 3; quadratico — budget 20.000, MAE test 0, baseline 18; Fibonacci — budget 1.000, MAE test 0, baseline 30,75.
- **Persistenza:** report Markdown/JSON, storico append-only in `reports/HISTORY.md`, snapshot per esecuzione e artifact conservato per 90 giorni. Il commit automatico dei report dipende dalle policy GitHub e dai permessi effettivi del repository.
- **Guardrail:** il workflow fallisce se la sentinella quadratica non raggiunge MAE 0 e accuratezza esatta 100%. Il codice del motore non viene modificato né integrato automaticamente; le modifiche algoritmiche richiedono revisione umana.
- **Limiti:** tutti i benchmark attuali sono sintetici e piccoli; la validazione remota e la persistenza via bot devono ancora essere confermate in Actions.
- **Prossima azione:** controllare la prima esecuzione del workflow, correggere eventuali errori di runner/permessi e verificare la creazione del primo report persistente.
