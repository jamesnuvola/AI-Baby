# AI Baby — automatic improvement report

- Run UTC: 2026-10-27T06:54:22.643131+00:00
- Commit: f2f78fb8045fe82bab5b65192a2738b40201d857
- Run: 5-attempt-1
- Python: 3.12.15
- Platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39
- Search depth: 3
- Budgets swept on seed 0: 1000, 5000, 20000
- Robustness seeds: 0, 1, 2

## Aggregate results across seeds

| Benchmark family | Frozen budget | Mean test MAE | Worst-seed MAE | Mean exact accuracy | Baseline mean MAE |
|---|---:|---:|---:|---:|---:|
| linear | 1000 | 0 | 0 | 100.0% | 4 |
| quadratic | 20000 | 0 | 0 | 100.0% | 19 |
| fibonacci | 1000 | 0 | 0 | 100.0% | 61.5 |
| geometric | 1000 | 0 | 0 | 100.0% | 960 |
| cubic_diagnostic | 20000 | 125.125 | 125.125 | 0.0% | 247 |

## Per-family diagnosis and next action

- **linear**: Extend to more seeds and real-world datasets; synthetic results alone do not establish generalization.
- **quadratic**: Selected budget reaches the ceiling: investigate pruning/search efficiency before increasing compute.
- **fibonacci**: Extend to more seeds and real-world datasets; synthetic results alone do not establish generalization.
- **geometric**: Extend to more seeds and real-world datasets; synthetic results alone do not establish generalization.
- **cubic_diagnostic**: At least one seed is not exact: inspect per-seed errors before claiming robust generalization.

## Method and limitations

- Budget is selected using seed-0 development metrics only; held-out test results do not select the configuration.
- The selected budget is frozen for all robustness seeds in that family.
- Families include linear, quadratic, Fibonacci, geometric, and cubic diagnostic sequences.
- Synthetic seeds are coefficient/initial-value variants, not independent real-world datasets.
- The cubic case is diagnostic: failure is recorded as a limitation, not hidden or used to tune against the test set.
- The workflow does not modify the search engine or merge algorithm changes automatically; changes require reviewed pull requests.
- Full per-seed metrics and timing are available in the JSON report.

