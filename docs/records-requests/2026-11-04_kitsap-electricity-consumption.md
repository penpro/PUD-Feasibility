# Public records request: Kitsap County electricity consumption data (2022 GHG inventory)

**Status:** DRAFT, not yet sent. Fill in the bracketed fields before sending.
**Prepared:** 2026-11-04
**Why:** The [Kitsap County 2022 GHG Emissions Analysis](../../data/SOURCES.md#s006--kitsap-county-2022-greenhouse-gas-emissions-analysis-v351)
(S006) was built from electricity consumption data "procured directly from the utilities that provide
service to each county," but it publishes only emissions. The load module currently back-calculates kWh
from those emissions. The answer moves by about ±20% depending on which emission factor the consultant used
(see `modules/01_load/results.md`, Method B). The underlying kWh would replace an estimate with a
measurement.

## Where to send it

| Priority | Agency | Why they likely hold it | How to submit |
|---|---|---|---|
| 1 | **WA Department of Commerce**, Growth Management Services (Climate program) | Funded and managed the county GHG analyses; its consultants (Cascadia Consulting Group, WSP) collected the utility data. | Commerce's public records request portal (linked from commerce.wa.gov → "Public records"). Confirm the current portal address on the site before submitting. |
| 2 | **Kitsap County Department of Community Development** | Publishes the report (kitsap.gov/dcd); may have received the data or deliverables for its climate planning. | Kitsap County's public records request portal (linked from kitsap.gov). Confirm the current address on the site before submitting. |

Send to both at once; they are independent agencies with independent records. Optional but often faster:
a short informal email to the Commerce climate planning staff listed in the report's acknowledgments, asking
whether the data can be shared without a formal request.

## Request text (copy from here)

> **To:** Public Records Officer, [Washington State Department of Commerce | Kitsap County]
> **From:** [NAME], [ORGANIZATION, or "on behalf of the Kitsap Public Power Feasibility Study, an independent open-source project"]
> **Contact:** [EMAIL] · [PHONE, optional]
> **Date:** [DATE]
>
> Under the Washington Public Records Act, chapter 42.56 RCW, I request copies of the following records
> relating to the *Kitsap County 2022 Greenhouse Gas Emissions Analysis* (Version 3.5.1, prepared for the
> Department of Commerce by Cascadia Consulting Group and partners; published by Kitsap County DCD as
> `CountyGHGAnalysisReport_Kitsap_20250630.pdf`):
>
> 1. **Electricity consumption data** (kWh or MWh) for Kitsap County for calendar year 2022, as provided by
>    Puget Sound Energy and any other electric utility (including Peninsula Light Company, Mason County PUD
>    No. 3, and the Bonneville Power Administration), broken down by sector or rate class (residential,
>    commercial, industrial, and any other categories such as street lighting), in the form received.
> 2. Any **monthly or other sub-annual** breakdown of the data in item 1, and the same data for any other
>    years collected (for example a baseline year).
> 3. Any **customer or account counts** by sector that accompanied the data in item 1.
> 4. The **emission factors** applied to electricity in the analysis: the utility-specific factor(s) for each
>    utility (value, units, year and source, including whether upstream emissions were included) and the
>    eGRID factor used for the location-based figure of 219,570 MTCO2e. Also any calculation workbooks,
>    ClearPath exports or data summaries showing how the 828,336 MTCO2e electricity total was computed.
> 5. **Natural gas consumption data** (therms) for Kitsap County for 2022 by sector, as provided by Cascade
>    Natural Gas or any other gas utility, plus any propane and fuel oil activity data used.
> 6. **Data request letters or emails** sent to the utilities for the data above, the utilities' transmittal
>    messages, and any data-sharing, confidentiality or non-disclosure agreements covering that data.
>
> I am requesting **aggregate, sector-level totals only**. I am not seeking any individual customer's
> name, address, account number or usage. If any responsive record contains customer-level information,
> please redact that portion and release the remainder.
>
> If you withhold or redact any record or portion, please cite the specific statutory exemption and briefly
> explain how it applies, as RCW 42.56.210(3) requires, and release all reasonably segregable non-exempt
> portions. If you intend to notify a third party under RCW 42.56.540 before release, please let me know
> the expected timeline.
>
> **Format:** electronic copies (original spreadsheet formats such as .xlsx or .csv preferred, or PDF)
> by email or download link. Installments are welcome; please send item 1 first if it is ready sooner.
>
> **Fees:** please notify me before incurring charges above $[25].
>
> Please confirm receipt and provide the estimated response time required by RCW 42.56.520. Thank you.
>
> [NAME]

## After sending

- Log the request in `docs/open-questions.md` under OQ-01 (date sent, agency, tracking number).
- When records arrive, save each file **unmodified** under `data/raw/records_requests/<agency>_<date>/`,
  register it in `data/sources.yaml` as a primary source, and run `python scripts/sources.py build`.
- Replace Method B's factor matrix with the actual kWh in `model/config.yaml` and relabel it VERIFIED.
  Keep the back-calculation as a cross-check.

## Parallel asks (separate requests; not drafted yet)

- **WA Utilities and Transportation Commission (UTC)**: PSE filings with Kitsap-area load or peak data,
  including PSE's Kitsap County non-wires-alternatives RFP and any Kitsap Peninsula transmission or
  distribution planning studies (OQ-05). The UTC is subject to the PRA; PSE may have designated parts of
  its filings confidential under RCW 80.04.095.
- **Puget Sound Energy**: PSE is a private company and not subject to the PRA. An informal request for
  Kitsap customer counts and MWh by rate class and month is still worth making, since PSE's own
  arguments rest on these numbers.
- **WA Public Disclosure Commission**: primary campaign-finance records for Prop 1 (PSE's reported
  ~$2.4M–$2.5M, OQ-08). These are online and need no request.
