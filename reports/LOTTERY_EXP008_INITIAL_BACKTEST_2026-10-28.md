# EXP-008 — primo confronto walk-forward su dati reali

**Data:** 2026-10-28  
**Stato:** esploratorio; implementazione e dataset in CI, nessun metodo promosso.  
**Scopo:** stabilire un riferimento riproducibile prima di provare ipotesi più insolite. Non è una dimostrazione di prevedibilità.

## Dataset congelati

- **SuperEnalotto:** 2.943 sestine dal 2009-01-02 al 2026-10-27. Le nove estrazioni più recenti sono state confrontate con l'archivio ufficiale; la base storica precedente deriva dal repository del progetto e non è stata verificata singolarmente contro ogni bollettino.
- **VinciCasa:** 3.390 cinquine giornaliere dal 2017-07-17 al 2026-10-27. L'ultima estrazione (concorso 300, 1-6-8-28-34) è stata verificata con l'archivio ufficiale.
- Fonti e SHA sono registrati nei manifesti JSON in `data/`.

## Protocollo

- Warm-up: prime 100 estrazioni; ogni previsione usa solo estrazioni strettamente precedenti al target.
- Valutazione per target: 2.843 sestine SuperEnalotto e 3.290 cinquine VinciCasa.
- Segmenti descrittivi: 2023–2024 e 2025–2026. Questi periodi sono già stati esaminati in precedenti ricerche SONAR: **non sono un holdout cieco nuovo**.
- Baseline uniforme teorica del numero medio di match: (6^2/90 = 0,4000) per SuperEnalotto; (5^2/40 = 0,6250) per VinciCasa.
- Regole confrontate senza scegliere un vincitore: frequenza globale, frequenza ultime 20, anti-hot ultime 20 (sceglie i numeri meno presenti), decadimento esponenziale τ=10 e ritardatari-first.
- I valori sono medie di match per singola sestina/cinquina; non sono probabilità di jackpot. I risultati riportati sono arrotondati a 4 decimali.

## SuperEnalotto — media di match (baseline 0,4000)

| Metodo | Tutto (N=2843) | 2023–2024 (N=390) | 2025+ esplorativo (N=380) |
|---|---:|---:|---:|
| Frequenza globale | 0,3894 | 0,3718 | 0,4395 |
| Frequenza ultime 20 | 0,3795 | 0,3667 | 0,4158 |
| Anti-hot ultime 20 | 0,3859 | 0,3590 | 0,4184 |
| Decadimento esponenziale τ=10 | 0,3827 | 0,3872 | 0,3737 |
| Ritardatari-first | 0,4077 | 0,3615 | 0,3947 |

**Lettura:** quattro metodi su cinque restano sotto la baseline sul totale; ritardatari-first la supera di appena 0,0077 match. La frequenza globale arriva a 0,4395 nel periodo 2025+, ma scende a 0,3718 nel 2023–2024. Il segnale non è stabile tra periodi e il blocco recente non è cieco: nessuna promozione.

## VinciCasa — media di match (baseline 0,6250)

| Metodo | Tutto (N=3290) | 2023–2024 (N=731) | 2025+ esplorativo (N=665) |
|---|---:|---:|---:|
| Frequenza globale | 0,6085 | 0,6047 | 0,5759 |
| Frequenza ultime 20 | 0,6219 | 0,5896 | 0,6301 |
| Anti-hot ultime 20 | 0,6216 | 0,6347 | 0,6105 |
| Decadimento esponenziale τ=10 | 0,6195 | 0,5896 | 0,6361 |
| Ritardatari-first | 0,6264 | 0,6689 | 0,6075 |

**Lettura:** le medie complessive sono sostanzialmente vicine alla baseline. Il valore 0,6689 dei ritardatari-first nel 2023–2024 scende a 0,6075 nel periodo 2025+; decadimento esponenziale e frequenza recente mostrano l'andamento opposto tra validation e periodo recente. È il profilo di risultati instabili che ci aspettiamo di vedere quando si esplorano molte varianti; non basta per inferire un vantaggio.

## Conclusione provvisoria

1. I cinque metodi semplici non mostrano un vantaggio stabile sui due giochi.
2. Il metodo controintuitivo anti-hot non domina il metodo hot/frequenza: cambia da periodo a periodo.
3. Nessun metodo è promosso e nessuna previsione di jackpot è stata dichiarata.
4. Il prossimo esperimento deve spostarsi oltre le sole frequenze: transizioni fra estrazioni, geometrie dei gap, codifiche posizionali, regimi e combinazioni di segnali. Le ipotesi vanno generate sul passato di sviluppo, poi congelate prima di ogni valutazione successiva.
5. Per SuperEnalotto resta da verificare individualmente lo storico anteriore al 13 ottobre 2026 contro i bollettini ufficiali.

## Riproducibilità

Comando per eseguire il benchmark completo (i risultati del runner comprendono distribuzioni di hit e baseline Monte Carlo):

```bash
python -m scripts.lottery_benchmark data/superenalotto_snapshot_2026-10-27.csv --game superenalotto --minimum-history 100 --simulations 500 --output reports/exp008-superenalotto.json
python -m scripts.lottery_benchmark data/vincicasa_snapshot_2026-10-27.csv --game vincicasa --minimum-history 100 --simulations 500 --output reports/exp008-vincicasa.json
```

Il report è append-only nel senso metodologico: i risultati negativi restano visibili; eventuali esperimenti futuri dovranno essere registrati separatamente, non sostituire queste misure.
