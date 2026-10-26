# Experiment log

Record each meaningful experiment as a new dated entry in `RESULTS_LOG.md` (do not silently overwrite previous outcomes).

For each run capture:
- experiment ID and date (UTC)
- code commit / version
- benchmark and data provenance
- train/development/test split fixed before evaluation
- search space, depth, budget, seed (if applicable)
- baseline(s)
- metrics on development and held-out test
- runtime, hardware, and any failures
- interpretation, limitations, and next action

Never use the held-out test set to select a candidate. If a test set is inspected repeatedly during development, label it as validation data and reserve a fresh test set.
