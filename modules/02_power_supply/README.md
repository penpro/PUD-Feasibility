# Module 2: Power supply

**Status:** not started.
**Tests PSE objection P-2:** "would lose access to cheap federal hydro … starting with none."
**Also tests D-3, D-4 and D-5** (clean-energy rules, gas and carbon, dam removal; see `docs/open-questions.md`).

## Questions

1. How much BPA Tier 1 (lowest-cost federal) power could a newly formed public utility get under BPA's
   post-2028 Provider of Choice contracts, and on what timeline? Partly answered (F-06, S035): new publics share
   200 aMW through Sept 30, 2044, at most 50 aMW per two-year rate period, first come, first served. Still open: KPUD's
   eligibility, how much of the limit would be left, and Tier 2 cost (OQ-06). KUOW's "200 megawatts" (S016) is this total.
2. What would the remainder cost: BPA Tier 2, bilateral contracts, market purchases? With what price risk?
3. How do shaping and capacity (winter peak ≈ 2× average) change the cost relative to an energy-only view?
4. What do CETA (clean-energy standards) and transmission/wheeling over PSE's or BPA's network add?
5. How much of a new utility's supply would be tied to gas and carbon prices, compared with PSE's (OQ-18)?
6. What would lower Snake River dam removal do to BPA's rates, if it happened during the contract period (OQ-19)?

## Inputs from other modules

Module 1: annual energy (central ~2.04 TWh; about 242 aMW including losses), monthly shape, peak range.

## Sensitivities to run

Planned ranges, not model inputs yet. Values enter `model/config.yaml` with labels when this module is built.

| Sensitivity | What we have so far | Traps to avoid |
|---|---|---|
| Natural gas price | Northwest Sumas averaged $1.87/MMBtu in 2024 through October and $1.59 in 2025 through August, with a record-low month of $0.56 (S030). | Those are historic lows, so they aren't a normal year, and one spike year isn't a trend. We still need a sourced annual series that includes 2022 (OQ-20). |
| Carbon allowance price | First auction Feb 28, 2023 at $48.50 (S029). Settled at $64.30 in Sept 2025 (S028) and $64.56 in June 2026 (S027). | No allowance cost existed before 2023. Reserve-auction prices aren't settlement prices (S028). Electric utilities are eligible for no-cost allowances (RCW 70A.65.120, S026), so auction price × emissions may overstate what customers pay. A new PUD's allocation is unknown (OQ-22). |
| Which plants | PSE's supply includes 665 MW from Grays Harbor and 700 MW from a converted Centralia (S025). KPUD has selected no power source (S002 p.4). | Price gas exposure on both sides of the comparison, never one side. Centralia doesn't run on gas until the conversion (late 2028 target, S033), and its heat rate depends on whether it is combined cycle (S025 says so; S033 doesn't; OQ-21). Fuel and carbon alone leave out O&M, pipeline and capacity costs. |
| Dam removal | Estimates of replacing the dams' benefits range from $10B to $31B (S032). | A long-term sensitivity, not a base case: the Army Corps says breaching needs action from Congress (S032). |

## Primary sources to collect

- BPA Provider of Choice policy and CHWM policy (collected: S035); Record of Decision and contract templates still to read
- BPA power and transmission rate schedules (current rate case)
- Jefferson PUD's BPA contract history (the most recent new public; it reached Tier 1 in 2013)
- Mid-C market price history (EIA wholesale data) for the market-exposure range
- Annual Northwest Sumas gas prices, including 2022
- PSE's Power Cost Adjustment filings (tariff Schedule 95) and the WUTC record on the Centralia agreement
- Ecology's no-cost allowance schedule for electric utilities
- BPA and Northwest Power and Conservation Council analyses of lower Snake River dam removal
