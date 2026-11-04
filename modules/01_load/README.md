# Module 1: Load

**Status:** v0 running. Preliminary, ESTIMATE-grade until measured Kitsap data arrives (OQ-01, OQ-05).
**Results:** [`results.md`](results.md), generated, never hand-edited.
**Code:** [`model/load.py`](../../model/load.py) · **Inputs:** [`model/config.yaml`](../../model/config.yaml) (`params.load`)

## Questions

1. How much energy does PSE deliver to Kitsap County customers each year, by class?
2. What is the average and peak demand, and the monthly shape?
3. How does it grow through 2045 (population, building electrification, EVs)?

## Scope

PSE's retail load in Kitsap County only. Excluded: BPA direct-service federal load (Naval Base Kitsap
Bremerton and Bangor), and the Kitsap customers of Peninsula Light and Mason PUD 3.

## Run

```bash
python -m model.load
```

Outputs: `data/processed/load/*.csv` and `results.md`.

## Current answer (2025)

Central **2.04 TWh/yr** (≈233 MW average at meter, ≈471 MW peak). Planning range 1.74–2.60 TWh; stress range
1.52–2.66 TWh. See `results.md` for every input and its label.

## To upgrade from ESTIMATE to VERIFIED

| Need | Source | Tracking |
|---|---|---|
| Measured 2022 kWh by sector (and month) | Commerce / Kitsap DCD records request | OQ-01 |
| Emission factor actually used | same request, item 4 | OQ-02, OQ-15 |
| PSE Kitsap customers by class | PSE, UTC | OQ-03 |
| Kitsap-area peak, observed and design | PSE non-wires RFP, IRP, UTC | OQ-05 |
| Hourly shape | EIA-930 balancing-authority hourly demand (PSEI) as a proxy, then PSE substation data | — |
| Gas therms by sector (electrification) | records request item 5 | OQ-12 |
| Light-duty vehicle count | WA DOL | OQ-09 |
