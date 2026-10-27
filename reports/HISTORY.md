
## Run 4-attempt-1 — 2026-10-26T21:05:09.231907+00:00

- **linear_3n_plus_2** — budget 1000; dev MAE 0; test MAE 0; next: Add independent seeds and a new held-out benchmark family before claiming generalization.
- **quadratic_n2_plus_1** — budget 20000; dev MAE 0; test MAE 0; next: Best development configuration uses the budget ceiling: investigate pruning/search efficiency before increasing compute.
- **fibonacci** — budget 1000; dev MAE 0; test MAE 0; next: Add independent seeds and a new held-out benchmark family before claiming generalization.

## Run 5-attempt-1 — 2026-10-27T06:54:22.643131+00:00

- **linear** — frozen budget 1000; mean test MAE 0; worst-seed MAE 0; next: Extend to more seeds and real-world datasets; synthetic results alone do not establish generalization.
- **quadratic** — frozen budget 20000; mean test MAE 0; worst-seed MAE 0; next: Selected budget reaches the ceiling: investigate pruning/search efficiency before increasing compute.
- **fibonacci** — frozen budget 1000; mean test MAE 0; worst-seed MAE 0; next: Extend to more seeds and real-world datasets; synthetic results alone do not establish generalization.
- **geometric** — frozen budget 1000; mean test MAE 0; worst-seed MAE 0; next: Extend to more seeds and real-world datasets; synthetic results alone do not establish generalization.
- **cubic_diagnostic** — frozen budget 20000; mean test MAE 125.125; worst-seed MAE 125.125; next: At least one seed is not exact: inspect per-seed errors before claiming robust generalization.
