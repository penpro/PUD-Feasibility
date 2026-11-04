# Kitsap Public Power Feasibility Study

An **independent, open-source** feasibility study of whether Kitsap Public Utility District (KPUD) could
take over electric service in Kitsap County, Washington from Puget Sound Energy (PSE). All data, the model
and the methodology are public so that anyone can audit, reproduce or challenge them.

**The question:** what would it cost, and what would customers' bills look like? The study does not tell
anyone how to vote or what KPUD should do. PSE's strongest objections are listed and tested directly
([open questions](docs/open-questions.md#pses-strongest-objections-and-where-this-study-tests-them)).

> Not affiliated with KPUD, PSE, or any campaign. Corrections and challenges are welcome: see
> [CONTRIBUTING.md](CONTRIBUTING.md).

**Plain-English version for voters:** <https://penpro.github.io/PUD-Feasibility/> (source: [docs/index.html](docs/index.html))
**What we need from you:** [Help wanted](docs/help-wanted.md), 20 specific asks sorted by who can help.

## Status (2026-11-04)

**KPUD Proposition 1** (Nov 3, 2026), unofficial: **No 60.50% (53,513), Yes 39.50% (34,935)**, with 45.1% of
registered voters tabulated (Nov 3, 8:02 PM count). The next count is due by 5 p.m. Nov 4 and certification
is Nov 24 ([tracker](data/processed/election/prop1_counts.csv)). If Prop 1 fails, KPUD's own feasibility
study "would not move forward" (KPUD Fact Publication). This project continues regardless.

| Module | Status |
|---|---|
| [1. Load](modules/01_load/) | **v0 running** ([results](modules/01_load/results.md)) |
| [2. Power supply](modules/02_power_supply/) | scoped |
| [3. Acquisition cost](modules/03_acquisition_cost/) | scoped |
| [4. Financing](modules/04_financing/) | scoped |
| [5. Operations](modules/05_operations/) | scoped |
| [6. Rates](modules/06_rates/) | scoped |
| [7. Local solar / DER](modules/07_solar_der/) | scoped |

## Preliminary findings (load only)

- PSE's Kitsap retail load is about **2.0 TWh/yr** (range 1.74–2.60; ≈233 MW average, ≈471 MW peak).
  Two independent methods land within about 10% of each other.
- The often-cited **3.24 TWh** is Washington's statewide per-capita average multiplied by Kitsap's
  population, not a measurement of Kitsap.
- Peak demand is the least certain number and the most important missing data.

Details, caveats and corrections to earlier figures: [docs/findings.md](docs/findings.md).

## Reproduce

Python 3.11+.

```bash
pip install -r requirements.txt
```

```bash
python scripts/sources.py verify
```

```bash
python -m model.load
```

```bash
python -m pytest -q
```

```bash
python scripts/build_site.py
```

`verify` checks every raw file against its SHA-256. `model.load` regenerates `data/processed/load/` and
`modules/01_load/results.md`. The tests re-derive config values from the raw EIA files and check the arithmetic.
`build_site` regenerates the website's numbers (`docs/site-data.js`) and `docs/help-wanted.md` from the model and
`docs/help-wanted.yaml`. A test fails if the site is out of date.

Track the Prop 1 count:

```bash
python scripts/fetch_election_results.py
```

## Layout

```
data/raw/            untouched source files (+ MANIFEST.sha256)
data/sources.yaml    source registry (edit this) -> data/SOURCES.md (generated)
data/processed/      model outputs
model/config.yaml    EVERY assumption, each labeled with source and date
model/               Python model (pandas)
modules/0N_*/        one folder per study module: scope, data needs, results
docs/                methodology, findings, open questions, records requests, and the
                     GitHub Pages site (index.html + generated site-data.js)
scripts/             source manifest and election tracker
tests/               provenance and arithmetic checks
```

## Evidence labels

Every number is **VERIFIED** (primary source), **ESTIMATE** (derived; method shown), **UNVERIFIED**
(untraced claim, used only to test it) or **ASSUMPTION** (stated judgment). The model will not run if a
number lacks a label, source and date. See [docs/methodology.md](docs/methodology.md).

## License

- Code: [MIT](LICENSE)
- Documentation and the study's processed data: [CC BY 4.0](LICENSE-CC-BY-4.0.txt)
- `data/raw/`: third-party files redistributed unmodified under their original terms (mostly U.S. federal
  and Washington public records). See [data/SOURCES.md](data/SOURCES.md).
