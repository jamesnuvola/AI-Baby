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

## EXP-005 — Validazione remota del ciclo automatico e correzione della persistenza

- **Stato:** workflow GitHub Actions verificato con esito positivo il 2026-10-26.
- **CI:** run #29 completato con esito `success` sul commit `b55d5075e7ca6164f652bbee628e1079bf0ca3e3`.
- **Continuous Improvement Lab:** run #4 completato con esito `success` sullo stesso commit; test unitari, sweep, riepilogo, persistenza del report e upload artifact tutti completati.
- **Esito benchmark remoto (Python 3.12.15):** lineare — budget 1.000, dev MAE 0, test MAE 0, baseline test MAE 3; quadratico — budget 20.000, dev MAE 0, test MAE 0, baseline 18; Fibonacci — budget 1.000, dev MAE 0, test MAE 0, baseline 30,75.
- **Diagnosi del primo tentativo di persistenza:** run #3 ha completato i benchmark ma il push del report è stato respinto perché `main` era avanzato dopo il checkout. L'artifact è stato comunque caricato.
- **Correzione:** aggiunto `git pull --rebase origin main` prima del push del report.
- **Verifica della correzione:** run #4 ha superato anche il passaggio di persistenza. Commit automatico creato: `5b3eb0a507ba8d41e759ec4deb47d3ca25cc6ded`, messaggio `ci: record benchmark run 4 [skip ci]`.
- **Prova persistente:** `reports/HISTORY.md`, `reports/benchmark-report.md` e `reports/history/run-4-attempt-1.json` sono presenti su GitHub; artifact `ai-baby-benchmark-report-4` caricato e non scaduto alla verifica.
- **Limiti:** test sintetici piccoli; la selezione di budget usa metriche di sviluppo, ma sono necessari più semi indipendenti e nuovi casi per valutare robustezza e generalizzazione.
- **Prossima azione prioritaria:** estendere la suite a più varianti indipendenti e metriche aggregate, mantenendo il codice del motore protetto da modifiche automatiche non revisionate.

## EXP-006 — Suite multi-seed e famiglie diagnostiche aggiuntive

- **Stato:** completato e verificato da GitHub Actions il 2026-10-27.
- **Commit testato:** `f2f78fb8045fe82bab5b65192a2738b40201d857`.
- **CI:** run #33 superato; test unitari, smoke test multi-seed e demo superati su Python 3.10, 3.11, 3.12 e 3.13.
- **Continuous Improvement Lab:** run #5 superato su Python 3.12.15; report JSON/Markdown generati e storico aggiornato su GitHub.
- **Protocollo:** sweep dei budget 1.000 / 5.000 / 20.000 sul seed 0; scelta tramite MAE di sviluppo, poi complessità e budget; budget congelato per i semi 0, 1 e 2. Nessuna metrica del test determina la selezione.
- **Famiglie e risultati (MAE test medio / accuratezza esatta media / baseline MAE medio):**
  - Lineare — budget 1.000; **0 / 100% / 4**.
  - Quadratica — budget 20.000; **0 / 100% / 19**.
  - Fibonacci — budget 1.000; **0 / 100% / 61,5**.
  - Geometrica — budget 1.000; **0 / 100% / 960**.
  - Cubica diagnostica — budget 20.000; **125,125 / 0% / 247**.
- **Esito positivo:** le quattro famiglie lineare, quadratica, Fibonacci e geometrica hanno mantenuto previsione esatta su tutti e tre i semi.
- **Esito negativo significativo:** la famiglia cubica non è stata appresa dal DSL corrente; MAE test 125,125 e accuratezza esatta 0%, pur migliorando la baseline (MAE 247). Questo è un limite concreto del motore, non un risultato da nascondere.
- **Diagnosi successiva:** il caso quadratico sceglie ancora il tetto di budget 20.000; il prossimo esperimento deve analizzare l'efficienza della ricerca e le cause del fallimento cubico, senza adattare il motore al test bloccato.
- **Limiti:** tre semi sintetici per famiglia non equivalgono a dati reali indipendenti e non provano generalizzazione nel mondo reale. Il test cubico è diagnostico e non ha influenzato la selezione.
- **Report persistente:** `reports/benchmark-report.md`, `reports/benchmark-report.json`, `reports/HISTORY.md` e snapshot per-run sotto `reports/history/`.


## EXP-007 — Diagnosi del limite cubico e candidato Newton di terzo ordine

- **Stato:** completato; CI e Continuous Improvement Lab superati il 2026-10-27.
- **Commit testato:** `a1cbdcccd70aa2c767ab3d47567df3d7f0294e80`.
- **CI:** run #36; i test e lo smoke test multi-seed sono stati eseguiti su Python 3.10–3.13.
- **Continuous Improvement Lab:** run #6 completato con esito `success`; report e storico persistiti su GitHub.
- **Motivazione:** EXP-006 aveva mostrato un MAE cubico di 125,125 e accuratezza esatta 0%; il candidato migliore disponibile era `((diff1 * 3) + mean)`.
- **Correzione:** aggiunto il candidato generale `newton3`, che estrapola usando le differenze finite di ordine 1, 2 e 3 degli ultimi quattro valori. Il criterio di selezione resta invariato.
- **Test unitari:** verificata l'estrapolazione su cubici con offset 0, 1 e 2 e il rifiuto di una storia troppo corta; il test end-to-end trova `newton3` e ottiene MAE test 0.
- **Risultati benchmark multi-seed (semi 0, 1, 2):**
  - Lineare — budget 1.000; MAE test medio 0; accuratezza esatta 100%; baseline MAE 4.
  - Quadratica — budget 1.000; MAE test medio 0; accuratezza esatta 100%; baseline MAE 19.
  - Fibonacci — budget 1.000; MAE test medio 0; accuratezza esatta 100%; baseline MAE 61,5.
  - Geometrica — budget 1.000; MAE test medio 0; accuratezza esatta 100%; baseline MAE 960.
  - Cubica diagnostica — budget 1.000; MAE test medio 0; accuratezza esatta 100%; baseline MAE 247.
- **Miglioramento osservato:** tutte e cinque le famiglie sintetiche sono state previste esattamente su tutti e tre i semi, e il budget selezionato per il caso quadratico è sceso da 20.000 a 1.000.
- **Limiti:** risultato circoscritto a cinque famiglie sintetiche e tre varianti ciascuna; non dimostra generalizzazione su dati reali o sequenze rumorose/non polinomiali. `newton3` è un bias matematico esplicito, non auto-riprogrammazione.
- **Report persistente:** `reports/benchmark-report.md`, `reports/benchmark-report.json`, `reports/HISTORY.md` e snapshot `reports/history/run-6-attempt-1.*`.
- **Prossimo esperimento prioritario:** test di stress su sequenze rumorose, cambi di regime e famiglie non polinomiali, per misurare quando `newton3` aiuta e quando porta a sovraestrapolazione; mantenere separati sviluppo e test bloccato.


## EXP-008 — Primo laboratorio su estrazioni reali: dati, baseline e metodi eterogenei

- **Stato:** primo confronto esplorativo registrato il 2026-10-28; il runner e i due dataset hanno superato la CI completa al commit `ff7ea60560c8fb40b82426ba2f0b418e19ea8a75` (test Python 3.10–3.13 e job benchmark su entrambi i giochi). Commit successivi in questa PR aggiornano report/documentazione.
- **Dataset persistenti:**
  - SuperEnalotto: `data/superenalotto_snapshot_2026-10-27.csv`, 2.943 sestine dal 2009-01-02 al 2026-10-27. Le nove estrazioni dal 13 al 27 ottobre sono state verificate contro l'archivio ufficiale; lo storico precedente proviene da uno snapshot di progetto e non è stato ricontrollato concorso per concorso.
  - VinciCasa: `data/vincicasa_snapshot_2026-10-27.csv`, 3.390 cinquine dal 2017-07-17 al 2026-10-27. Ultima estrazione 1-6-8-28-34 verificata nell'archivio ufficiale.
  - Manifesti JSON con provenienza, SHA e limiti: `data/*manifest.json`.
- **Infrastruttura aggiunta:** validazione CSV e regole dei due giochi, scoring dei match, baseline uniforme teorica e Monte Carlo riproducibile, valutatore rolling-origin senza leakage, importatore dello storico SuperEnalotto, cinque euristiche eterogenee e runner di benchmark.
- **Metodi confrontati:** frequenza globale, frequenza ultime 20, anti-hot ultime 20, decadimento esponenziale τ=10 e ritardatari-first. Le previsioni sono valutate solo contro estrazioni successive alla rispettiva storia disponibile.
- **Baseline teorica:** SuperEnalotto 0,4000 match medi per sestina; VinciCasa 0,6250 match medi per cinquina.
- **Risultati esplorativi:** vedi `reports/LOTTERY_EXP008_INITIAL_BACKTEST_2026-10-28.md`. SuperEnalotto: medie complessive 0,3795–0,4077; nessuna regola mostra vantaggio stabile fra i segmenti. VinciCasa: medie complessive 0,6085–0,6264; il metodo ritardatari-first passa da 0,6689 nel 2023–2024 a 0,6075 nel 2025+, mentre altre regole cambiano anch'esse direzione tra periodi.
- **Interpretazione:** nessun metodo promosso e nessuna capacità predittiva dimostrata. Le finestre 2023–2024 e 2025+ sono state già esplorate in precedenti ricerche SONAR, quindi non costituiscono un test cieco nuovo. Le differenze sono descrittive e soggette a selezione multipla.
- **Prossimo esperimento:** esplorare transizioni, gap, codifiche posizionali, regimi e interazioni non convenzionali; congelare le ipotesi prima delle verifiche prospettiche e conservare tutti gli esiti, anche negativi.


## EXP-009 — Analogie di transizione e geometria dei gap

- **Stato:** metodi implementati; unit test superati da GitHub Actions al commit `ef64ce0100fcb1b7ae6a5f09e6cb6dee7d24c311`. La CI aggiornata con verifica del freeze prospettico è in corso nella PR #4.
- **Metodi:** `transition_analogue` vota i numeri delle estrazioni-successore di stati storici con overlap almeno 2, peso overlap^3; `gap_trajectory_neighbours` trova i 20 stati con geometria dei gap più vicina (distanza L1) e vota i loro successori con peso 1/(1+distance).
- **SuperEnalotto (baseline 0,4000):** transition analogue — 0,4034 su tutto il periodo, 0,3974 nel 2023–2024, 0,3868 nel 2025+; gap nearest20 — 0,3887, 0,4385, 0,3737. Nessun vantaggio stabile.
- **VinciCasa (baseline 0,6250):** transition analogue — 0,6249, 0,6553, 0,6361; gap nearest20 — 0,6261, 0,6279, 0,6797 rispettivamente su tutto, 2023–2024 e 2025+.
- **Osservazione interessante ma non confermativa:** VinciCasa gap nearest20 nel periodo 2025+ ha 93/665 target con almeno 2 hit (13,98%), contro circa 10,88% atteso uniformemente. Lo scarto nominale è circa 2,57 deviazioni standard su questa singola metrica; dopo molti metodi/segmenti/metriche e dato che il periodo era già esplorato, non è evidenza indipendente e non si promuove il metodo.
- **Report persistente:** `reports/LOTTERY_EXP009_STRUCTURAL_ANALOGUES_2026-10-28.md`.

## EXP-010 — Freeze prospettico pre-estrazione

- **Stato:** record congelato alle 2026-10-28 11:06:13 Europe/Rome; verifica automatica del freeze aggiunta al workflow CI.
- **Target:** VinciCasa 2026-10-28 e SuperEnalotto 2026-10-29; cutoff dati 2026-10-27.
- **Record immutabile:** `reports/PREDICTION_FREEZE_2026-10-28.md` e `reports/prediction-freeze-2026-10-28.json`.
- **Metodi congelati:** frequenza globale, frequenza ultime 20, anti-hot, decadimento esponenziale, ritardatari-first, transition analogue, gap-trajectory nearest20 e controllo uniforme seed 0.
- **Regola:** dopo ogni estrazione si valutano tutti i metodi; non eliminare né ritoccare retroattivamente un metodo in base all'esito. Una singola estrazione non può confermare un vantaggio.
- **Scopo:** iniziare un shadow test prospettico con cutoff e previsioni verificabili, non raccomandare puntate.
