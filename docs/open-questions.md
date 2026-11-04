# Open questions

Stable IDs (OQ-nn) are cited from the model, results and docs. Never renumber; close an item by
recording the answer and its source. **P1** = changes a headline number, **P2** = changes a module,
**P3** = context.

| ID | Pri | Question | Why it matters | Next step | Status |
|---|---|---|---|---|---|
| OQ-01 | P1 | What were PSE's actual 2022 Kitsap kWh by sector (and by month)? | Replaces Method B's back-calculation with a measurement. | [Records request draft](records-requests/2026-11-04_kitsap-electricity-consumption.md) to Commerce + Kitsap DCD. | Drafted 2026-11-04; PDF letters ready, not sent |
| OQ-02 | P1 | Which electricity emission factor(s) did the GHG inventory apply, and was any non-PSE utility included? | The factor choice moves Method B by about ±20%. A single factor is also what lets us split kWh by sector. | Records request item 4. | Open |
| OQ-03 | P1 | How many PSE customers are in Kitsap, by rate class? | Method C's largest structural input. PSE's "130,000" is rounded and came from an advocacy release. | Ask PSE directly; check UTC filings and PSE community reports. | Open |
| OQ-04 | P2 | Are Naval Base Kitsap Bremerton and Bangor still BPA direct-service customers? Does PSE serve any federal load as retail? | Defines what KPUD would and would not take over. Federal loads are large. | BPA customer list; Navy (NAVFAC NW) utility contracts; EIA-861 BPA detail. Source S013 is from 2016. | Open |
| OQ-05 | P1 | What is the PSE Kitsap-area peak demand, observed and weather-normalized (1-in-10)? | Peak sets substation, transmission and BPA capacity needs. The module's peak range (342–738 MW) is wide. | PSE's Kitsap non-wires-alternatives RFP; PSE IRP area forecasts; UTC records request; BPA transmission planning. | Open |
| OQ-06 | P1 | How much BPA Tier 1 power could a new Kitsap PUD actually get, and when? KUOW says "200 megawatts" for public utilities. | PSE's "starting with none" claim vs. KUOW's 200 MW. This is the core of the power-supply module. | BPA Provider of Choice policy and contract documents on new-public allocations (primary). | Open |
| OQ-07 | P2 | Is there any primary source for a $1.2B–$1.5B (or ~$1.5B) Kitsap acquisition value? | Widely repeated, never sourced. A search summary attributed it to a PSE-hired consultant, but S018 and S019 contain no such figure. | Search PSE and campaign materials and PDC filings; ask PSE for the study. Do not use until sourced. | Open |
| OQ-08 | P3 | How much did each side spend on Prop 1? | Context only, not used in the model. | PDC filings (S024, `scripts/fetch_campaign_finance.py`): No committee raised $2,401,233 (PSE $2,318,178, 96.5%) and spent $2,304,528; Yes committee (Unplug PSE) raised $9,055 and spent $7,253. Rerun the script after post-election reports. | Answered 2026-11-04 (filings through Oct 27) |
| OQ-09 | P2 | How many light-duty vehicles are registered in Kitsap? | Turns the EV-stock scenarios into adoption shares, so they can be checked against state ZEV targets. | WA DOL registration counts by county. | Open |
| OQ-10 | P3 | Final certified Prop 1 result. | Status of KPUD's own study: a "No" means KPUD's study "would not move forward" (S002). | `python scripts/fetch_election_results.py` after each count; canvass certifies 2026-11-24 9 a.m. (S005). | Unofficial: No 60.50% (Nov 3, 8:02 PM, 45.1% of registered voters tabulated) |
| OQ-11 | P2 | Jefferson PUD precedent from primary sources: purchase price and adjustments, separation costs, financing, rates before and after. | The only modern WA precedent. Current figures come from news coverage (S020). | UTC order approving the PSE sale; Jefferson PUD audited financials; State Auditor reports. | Open |
| OQ-12 | P2 | Kitsap natural-gas therms by sector. | Converts the electrification growth assumption into a derived estimate. | Records request item 5. | Open |
| OQ-13 | P2 | How many Kitsap customers do Peninsula Light and Mason PUD 3 serve? | Separates their load from any county-wide figure. | Ask both utilities (public; PRA applies to Mason PUD 3). | Open |
| OQ-14 | P3 | What did KPUD present to its board (recordings, slides, consultant memos) before placing Prop 1? | May contain load, cost or BPA information already gathered. | Review KPUD "Recordings, Presentations & Board Documents" (S001). | Open |
| OQ-15 | P2 | eGRID cross-check: which eGRID factor produced 219,570 tCO2e? | The NWPP rate implies an impossible PSE factor. The WA-state rate implies ~2.6 TWh. Resolving this would settle Method B. | Records request item 4. | Open |

## PSE's strongest objections, and where this study tests them

Taken from PSE's own release (S018) and quoted coverage (S016). Each one gets a direct, quantified test.
None is dismissed.

| # | Objection (PSE) | Test | Module |
|---|---|---|---|
| P-1 | KPUD has no public plan to fund, operate, maintain or power a ~130,000-customer utility. | This study is that plan's evidence base. Each module must produce numbers with ranges. | all |
| P-2 | KPUD would lose access to cheap federal hydro and would have to buy all its energy, "starting with none." | Size BPA Tier 1 availability for a new public (OQ-06) against this module's 2.04 TWh / ~240 aMW central load. Price the remainder at Tier 2 or market, with ranges. | 2 |
| P-3 | There would be a "massive cost" to buy PSE's system. Jefferson proponents estimated $47M and the final cost was $109M. | Value Kitsap assets from PSE's FERC Form 1 and UTC rate-base filings. Model condemnation and separation costs. Test how the Jefferson estimate grew, and why, from primary documents (OQ-11). | 3 |
| P-4 | KPUD has no experience running an electric utility this size. | Staffing and O&M benchmarks from utilities of similar size (EIA-861; PUD annual reports). Contract-operations options. | 5 |
| P-5 | Storm response: PSE has 70+ employees and 50+ Potelco contractors (34 line workers) in Kitsap and can draw on crews across the West. | Crew sizing, mutual-aid agreements (WPUDA/NWPPA), and EIA-861 reliability data (SAIDI/SAIFI) for PSE vs. Washington PUDs. | 5 |
| P-6 | Leaving PSE would not lower prices. | Apples-to-apples bill comparison at identical usage, including acquisition debt service and power-supply risk. | 6 |
