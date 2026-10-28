# Lottery research protocol — EXP-008

## Scope
This lab tests whether historical main-number draws contain reproducible out-of-sample predictive signal for SuperEnalotto or VinciCasa. It does not assume that signal exists. These games are evaluated independently.

## Canonical dataset CSV
UTF-8 CSV with this header:

```csv
draw_id,date,game,numbers
SE-2026-001,2026-01-02,superenalotto,4 12 25 48 66 81
VC-2026-001,2026-01-03,vincicasa,3 11 19 27 35
```

- `draw_id`: unique, stable draw identifier.
- `date`: ISO `YYYY-MM-DD`.
- `game`: `superenalotto` or `vincicasa`.
- `numbers`: main numbers only, separated by spaces. Exclude supplementary numbers (e.g. Jolly/SuperStar) from the primary six-number target.
- Rows must be chronological. Keep source URL, retrieval date, and any corrections in a separate provenance manifest before analysis.
- Do not mix games or silently repair invalid rows. Fail fast and document corrections.

## Baselines and metrics
- Uniform subset baseline: expected number of main-number hits is (k^2/N), where (k) is the number of drawn main numbers and (N) the pool size.
- Monte Carlo baseline: repeat random uniform predictions with a fixed, recorded seed and report the distribution of mean hits.
- Report per-draw hits, mean hits, exact-match distribution, and uncertainty. Never compare a selected model only against one lucky random ticket.
- If ranking probabilities are available, evaluate proper scoring rules as well as hit counts.

## Walk-forward protocol
For every target draw, a predictor receives only strictly earlier draws. Store prediction, timestamp, code revision, model/configuration, seed, and target draw ID before the result is appended. Split chronologically into development, validation and a final untouched period. Use rolling-origin evaluation inside development; do not repeatedly inspect the final period to choose methods.

## Experimental freedom with statistical controls
Explore conventional and non-conventional ideas, including position-aware representations, gaps, modular transforms, co-occurrence networks, ensembles, randomized/evolutionary hypothesis search, and surrogate/null datasets. Record all runs, not only winners. Correct for multiple comparisons and require independent or prospective confirmation before claiming an edge.

## Current implementation status
`ai_baby/lottery.py` supplies data validation, CSV loading, exact-hit scoring, a reproducible uniform Monte Carlo baseline, and a generic rolling-origin evaluator. Unit tests cover these primitives. No real lottery dataset or positive predictive edge is claimed by this module. Dataset acquisition and provenance verification are the next gate.

## Initial source audit (2026-10-28)
- SuperEnalotto candidate source: [jamesnuvola/Superenalotto `src/data/draws.js`](https://github.com/jamesnuvola/Superenalotto/blob/main/src/data/draws.js). Its documented rows cover 2009 onward, but the checked snapshot currently ends on 2026-10-10 (2,934 rows). It is therefore **not current enough** for a production backtest without refreshing and checking against the official archive.
- Official SuperEnalotto archive: https://www.superenalotto.it/archivio-estrazioni . It exposes the main six numbers plus supplementary Jolly/SuperStar; only the main six are the primary target.
- Official VinciCasa archive: https://www.vincicasa.it/archivio-estrazioni . It offers recent draws and year-based historical archives; the data needs to be acquired and validated separately.
- Import helper: `python -m scripts.import_superenalotto_js path/to/draws.js data/superenalotto.csv`. It parses the documented source format and intentionally excludes Jolly/SuperStar. The importer does not download data or certify the source as complete.
- No historic rows are copied into this repository yet. Keep source snapshots and their retrieval dates explicit; never treat a source's claimed “historical” coverage as verified completeness.
