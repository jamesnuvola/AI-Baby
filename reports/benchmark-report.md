# AI Baby — automatic improvement report

- Run UTC: 2026-10-26T21:05:09.231907+00:00
- Commit: `b55d5075e7ca6164f652bbee628e1079bf0ca3e3`
- Run: `4-attempt-1`
- Python: 3.12.15
- Platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39
- Search depth: 3
- Budgets swept: 1000, 5000, 20000

## Results

| Benchmark | Selected budget | Development MAE | Held-out test MAE | Baseline test MAE | Exact test accuracy |
|---|---:|---:|---:|---:|---:|
| linear_3n_plus_2 | 1000 | 0 | 0 | 3 | 100.0% |
| quadratic_n2_plus_1 | 20000 | 0 | 0 | 18 | 100.0% |
| fibonacci | 1000 | 0 | 0 | 30.75 | 100.0% |

## Diagnosi e prossima azione

- **linear_3n_plus_2**: Add independent seeds and a new held-out benchmark family before claiming generalization.
- **quadratic_n2_plus_1**: Best development configuration uses the budget ceiling: investigate pruning/search efficiency before increasing compute.
- **fibonacci**: Add independent seeds and a new held-out benchmark family before claiming generalization.

## Interpretazione e limiti

- Le configurazioni sono selezionate usando soltanto metriche di sviluppo; il test bloccato non sceglie il budget.
- Il benchmark quadratico è un controllo di regressione sintetico, non una prova di capacità predittiva nel mondo reale.
- I casi lineare e Fibonacci sono diagnostici esplorativi; non autorizzano affermazioni di generalizzazione.
- Il workflow non modifica il codice sorgente né integra modifiche automaticamente. Ogni cambiamento dell'algoritmo richiede una pull request revisionata.
- I dettagli completi sono nel JSON allegato.

