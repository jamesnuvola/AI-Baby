# AI Baby 0.2

Experimental cognitive research prototype for exploring and testing expression-search hypotheses against synthetic sequences.

## Status

This repository is an experimental prototype. A successful synthetic-sequence demonstration is not evidence of general predictive ability. Results must be evaluated against baselines and held-out data.

## Local setup

Requires Python 3.11 or newer.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Research principles

- Keep experiment inputs, methods, and outcomes reproducible.
- Compare against simple baselines.
- Separate training/history data from held-out evaluation.
- Record failures and limitations as well as successes.
- Never interpret a fit to synthetic data as proof of real-world prediction.

## Project contents

The repository will hold the prototype, unit tests, continuous integration workflow, Codespaces configuration, and an append-only experiment log.
