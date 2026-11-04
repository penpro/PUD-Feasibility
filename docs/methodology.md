# Methodology

## The question

What would it cost for Kitsap PUD to provide electric service in PSE's Kitsap County service area, and
what would customers' bills look like compared with staying on PSE? The study answers that question
with ranges. It does not recommend a vote or an outcome.

## Rules every number follows

### Evidence labels

| Label | Meaning | Example |
|---|---|---|
| **VERIFIED** | Taken directly from a primary source, which is cited. | 828,336 tCO2e electricity emissions, 2022 (S006, Table 2) |
| **ESTIMATE** | Derived by this study. The method is shown in code and in the `note`. | kWh back-calculated from emissions ÷ PSE carbon intensity |
| **UNVERIFIED** | A claim not traced to a primary source. Used only to test it, never as an input to a result. | FindEnergy's 3,236,601 MWh; KUOW's "370 megawatts" |
| **ASSUMPTION** | Modeler judgment with stated reasoning. These are the first things to challenge. | EV stock in 2035 |

The brief defined three labels. ASSUMPTION was added because a judgment call is not "derived," and
calling it an ESTIMATE would overstate how much evidence stands behind it.

### Source kinds

**primary** (the agency or utility that produced the number) · **secondary** (journalism) ·
**third-party** (aggregators with undisclosed methods) · **advocacy** (a party to the debate speaking
for itself; PSE's releases are primary for PSE's own operating facts and advocacy for everything else).

### How provenance is enforced, not just described

1. **`data/sources.yaml`** registers every source. `python scripts/sources.py build` hashes every file
   under `data/raw/` into `data/raw/MANIFEST.sha256` and renders `data/SOURCES.md`. `verify` fails if a
   raw file was changed, is unregistered, or is missing. Raw files are excluded from git line-ending
   normalization (`.gitattributes`), so their hashes survive a clone.
2. **`model/config.yaml`** holds every number the model uses. `model.common.load_config()` refuses to run
   if any parameter lacks a label, unit, source ID or date, if a source ID is unknown, or if an
   ESTIMATE/ASSUMPTION/UNVERIFIED value has no note. A bare number is a validation error.
3. **Values derived from data files are re-derived by tests.** For example, `tests/test_config.py`
   recomputes the EIA benchmark values from the raw EIA workbooks and fails if the config drifts.
4. **Results documents are generated.** `modules/01_load/results.md` is written by `python -m model.load`,
   so the published numbers cannot drift from the code.

### Ranges, not points

- A range parameter's `low/central/high` are the parameter's own values. Code maps them to load direction:
  for example, a *higher* emission factor gives *lower* kWh, and a *lower* load factor gives a *higher* peak.
- **Planning range** (low/central/high): the range we think is realistic.
- **Stress range**: every uncertain input set to its worst end at once (corner combinations). It is
  deliberately wide and is a bound, not a forecast.
- **One-at-a-time sensitivity** shows which input matters most.

### The central rule (judgment, stated once)

Where no Kitsap-specific value exists, central = the midpoint of **PSE system-wide** (urban and suburban,
largely gas-heated) and **Jefferson PUD** (a former PSE territory on the same peninsula, with little gas
service). Kitsap is assumed to sit between them. This applies to residential and commercial use per
customer, loss fraction and load factor.

### Units

- Ecology carbon intensity: gCO2e/MJ → tCO2e/MWh = × 3,600 MJ/MWh ÷ 10⁶ g/t = **× 0.0036**.
  (Ecology's tables are headed gCO2e/MJ while one sentence of body text says "per ... kWh". We follow the
  tables and the Clean Fuel Standard convention. Read as per-kWh, PSE's factor would be implausibly low.)
- 1 tonne = 2,204.62 lb. Average MW = MWh ÷ 8,760 (2025 and 2022 are not leap years).
- "At meter" = retail sales. "Incl. losses" = retail ÷ (1 − loss fraction), the energy KPUD would have to buy.

## Module 1: Load

**Scope:** PSE's retail load in Kitsap County. EIA-861 lists four utilities serving Kitsap County: PSE,
BPA (federal direct service; BPA's own 2016 slides say "Bremerton and Bangor are direct served by BPA"),
Peninsula Light and Mason PUD 3. Only PSE's load would transfer in an acquisition of PSE's system.

**Method A: FindEnergy (tested, rejected).** 3,236,601 MWh ÷ 277,673 people = 11.656 MWh/person, which
is FindEnergy's *statewide* per-capita figure (11.66) and appears unchanged on other county pages. It is a
population-scaled state average. It is not a measurement of Kitsap, and it is reported only to explain why
it is wrong.

**Method B: GHG inventory back-calculation (2022).** kWh = sector tCO2e (S006) ÷ PSE carbon intensity
(Ecology CFS, S007–S009). The inventory does not say which PSE factor it used, so all six plausible
factors are shown: fuel-mix year 2021/2022/2023 × lifecycle total or production-to-consumption only.
Central = 2022 mix, production-to-consumption, for three reasons: it matches the inventory year, it is the
component that includes T&D losses (which the report says were included), and community inventories
normally leave out upstream fuel-cycle emissions. Low/high = the largest and smallest factors. The sector
split assumes one factor for all sectors. Results are scaled 2022 → 2025 by OFM population with
per-customer use held flat.

*eGRID cross-check:* the report's location-based figure (219,570 tCO2e) divided by eGRID2022 rates gives
0.80 TWh at the NWPP rate. That would require a PSE factor of about 288 gCO2e/MJ, roughly twice anything
published, so NWPP was probably not applied to the same kWh. The Washington state rate gives 2.60 TWh. The
check leans toward the upper half of the range but cannot settle it (OQ-15).

**Method C: bottom-up (2025).** customers × residential share × residential MWh/customer + commercial
remainder × commercial MWh/customer, plus a 0.36% industrial uplift taken from the inventory's sector
ratio. Benchmarks are EIA-861 2025 values for PSE system-wide, Jefferson PUD, Mason PUD 3 and Clallam
PUD. Peninsula Light is excluded for commercial use, because it books small commercial accounts as
residential (518 MWh per commercial customer).

**Reconciliation.** Central = mean of B central and C central. Low/high = B's envelope. Stress = C's corners.
B and C share no inputs except the small industrial uplift, so their agreement is a real check.

**Peak.** retail ÷ (1 − loss) ÷ 8,760 ÷ load factor. Load factors come from 2025 EIA-861 peaks:
Jefferson 0.427 (low, so higher peak) to PSE system 0.603. These are observed peaks, not design peaks.

**Monthly shape.** PSE system-wide billed sales by class, averaged over 2022–2025 (EIA-861M) and applied
to Kitsap's class totals. Limitations: billing lag (about half a month), and PSE's system is probably less
winter-peaking than Kitsap.

**Projections.** OFM population growth × linear change in per-customer use to 2045 + an EV adder above the
2026 registered fleet (WA DOL). The load factor is held constant, which is a known simplification.

## Modules 2–7

Planned methods and data needs are in each `modules/0N_*/README.md`. Same rules apply: config-driven,
labeled, ranged, and PSE's objections tested directly (see `docs/open-questions.md`).

## Known limitations of v0

- No Kitsap-specific measured load yet (OQ-01, OQ-05). Every load number is an ESTIMATE.
- The customer count (130,000) is PSE's rounded figure from an advocacy release (OQ-03).
- Peaks are not weather-normalized. A planning peak would be higher than the observed-year peak.
- Growth parameters are ASSUMPTIONS pending gas-therm data (OQ-12) and vehicle counts (OQ-09).
