# EXP-009 — analogie di transizione e geometria dei gap

**Data:** 2026-10-28  
**Stato:** esploratorio; metodi e test unitari superati nella CI al commit `ef64ce0100fcb1b7ae6a5f09e6cb6dee7d24c311`.  
**Ipotesi:** le estrazioni con sovrapposizioni o geometrie dei gap simili possono avere transizioni successive informative. È un'ipotesi da confutare, non un'assunzione.

## Metodi congelati prima del confronto
1. **Transition analogue:** per ogni stato storico si calcola la sovrapposizione con l'ultima estrazione disponibile; se è almeno 2, i numeri della successiva estrazione storica ricevono un voto proporzionale a (overlap^3).
2. **Gap-trajectory nearest20:** si rappresentano i numeri ordinati tramite i gap, inclusi i margini 1..N; si scelgono i 20 stati storici con distanza L1 minima e si votano i numeri delle rispettive estrazioni successive con peso (1/(1+distance)).
3. Fallback deterministico sulla frequenza globale solo se non esistono voti.

Ogni previsione usa esclusivamente estrazioni precedenti. Warm-up 100; nessuna selezione di parametri basata sul segmento 2025+.

## Risultati — SuperEnalotto

Baseline uniforme teorica: **0,4000 match medi** per sestina.

| Metodo | Tutto (N=2843) | 2023–2024 (N=390) | 2025+ esplorativo (N=380) |
|---|---:|---:|---:|
| Transition analogue | 0,4034 | 0,3974 | 0,3868 |
| Gap-trajectory nearest20 | 0,3887 | 0,4385 | 0,3737 |

**Esito:** nessun vantaggio stabile. La geometria dei gap è sopra la baseline nel segmento 2023–2024, ma sotto nel segmento più recente; il transition analogue è vicino alla baseline sul totale e scende nel periodo recente.

## Risultati — VinciCasa

Baseline uniforme teorica: **0,6250 match medi** per cinquina.

| Metodo | Tutto (N=3290) | 2023–2024 (N=731) | 2025+ esplorativo (N=665) |
|---|---:|---:|---:|
| Transition analogue | 0,6249 | 0,6553 | 0,6361 |
| Gap-trajectory nearest20 | 0,6261 | 0,6279 | 0,6797 |

Per il metodo gap-trajectory nearest20 nel segmento 2025+, la distribuzione 0/1/2/3/4/5 hit è **315/257/84/9/0/0**. Quindi 93/665 (13,98%) hanno almeno 2 hit. Il riferimento uniforme teorico è circa 10,88%, ossia circa 72,3 casi attesi; lo scarto nominale è circa 2,57 deviazioni standard per questo singolo indicatore.

### Perché questo NON è ancora un risultato predittivo confermato
- Sono stati confrontati più metodi, segmenti e metriche: la ricerca multipla rende gli scarti migliori del caso più probabili.
- Il periodo 2025+ è stato già esplorato in analisi SONAR precedenti, perciò non è un holdout cieco indipendente.
- La media complessiva del metodo gap-trajectory è 0,6261, praticamente identica alla baseline 0,6250; il miglioramento apparente è concentrato nel segmento recente.
- L'ipotesi può fallire sul prossimo blocco di estrazioni.

**Decisione:** non promuovere né dichiarare vantaggio. Conservare il metodo come candidato sperimentale e valutarlo in shadow test prospettico con predizioni congelate prima delle estrazioni. Il freeze del 28 ottobre include tutti i metodi, non soltanto questo candidato, per impedire di cambiare retroattivamente la regola valutata.

## Prossimo passo
Mantenere tutte le previsioni pre-estrazione per almeno un blocco prospettico preregistrato; riportare ogni estrazione, tutti i metodi, il controllo casuale e la distribuzione dei match. Una sola estrazione futura non può confermare o smentire la capacità predittiva.
