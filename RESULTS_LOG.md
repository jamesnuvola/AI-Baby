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
