# AI Baby — automatic improvement report

- Run UTC: 2026-10-29T11:42:26.643102+00:00
- Commit: 843635e34d82bbe7a0af57a35344089844298eb7
- Run: 19-attempt-1
- Python: 3.12.15
- Platform: Linux-7.0.0-1017-azure-x86_64-with-glibc2.39
- Search depth: 3
- Budgets swept on seed 0: 1000, 5000, 20000
- Robustness seeds: 0, 1, 2

## Aggregate results across seeds

| Benchmark family | Frozen budget | Mean test MAE | Worst-seed MAE | Mean exact accuracy | Baseline mean MAE |
|---|---:|---:|---:|---:|---:|
| linear | 1000 | 0 | 0 | 100.0% | 4 |
| quadratic | 1000 | 0 | 0 | 100.0% | 19 |
| fibonacci | 1000 | 0 | 0 | 100.0% | 61.5 |
| geometric | 1000 | 0 | 0 | 100.0% | 960 |
| cubic_diagnostic | 1000 | 0 | 0 | 100.0% | 247 |

## Per-family diagnosis and next action

- **linear**: Extend to more seeds and real-world datasets; synthetic results alone do not establish generalization.
- **quadratic**: Extend to more seeds and real-world datasets; synthetic results alone do not establish generalization.
- **fibonacci**: Extend to more seeds and real-world datasets; synthetic results alone do not establish generalization.
- **geometric**: Extend to more seeds and real-world datasets; synthetic results alone do not establish generalization.
- **cubic_diagnostic**: Extend to more seeds and real-world datasets; synthetic results alone do not establish generalization.

## Method and limitations

- Budget is selected using seed-0 development metrics only; held-out test results do not select the configuration.
- The selected budget is frozen for all robustness seeds in that family.
- Families include linear, quadratic, Fibonacci, geometric, and cubic diagnostic sequences.
- Synthetic seeds are coefficient/initial-value variants, not independent real-world datasets.
- The cubic case is diagnostic: failure is recorded as a limitation, not hidden or used to tune against the test set.
- The workflow does not modify the search engine or merge algorithm changes automatically; changes require reviewed pull requests.
- Full per-seed metrics and timing are available in the JSON report.

