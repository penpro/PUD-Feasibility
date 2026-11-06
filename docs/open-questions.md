# Open questions

Stable IDs (OQ-nn) are cited from the model, results and docs. Never renumber; close an item by
recording the answer and its source. **P1** = changes a headline number, **P2** = changes a module,
**P3** = context. The biggest gaps have a step-by-step plan under [Plans to close the gaps](#plans-to-close-the-gaps).

| ID | Pri | Question | Why it matters | Next step | Status |
|---|---|---|---|---|---|
| OQ-01 | P1 | What were PSE's actual 2022 Kitsap kWh by sector (and by month)? | Replaces Method B's back-calculation with a measurement. | [Records request draft](records-requests/2026-11-04_kitsap-electricity-consumption.md) to Commerce + Kitsap DCD. | Sent 2026-11-04 2:30 PM to Commerce and Kitsap County; first responses due by Nov 12 (RCW 42.56.520) |
| OQ-02 | P1 | Which electricity emission factor(s) did the GHG inventory apply, and was any non-PSE utility included? | The factor choice moves Method B by about ±20%. A single factor is also what lets us split kWh by sector. | Records request item 4. | Open |
| OQ-03 | P1 | How many PSE customers are in Kitsap, by rate class? | Method C's largest structural input. PSE's "130,000" is rounded and came from an advocacy release. | Ask PSE directly; check UTC filings and PSE community reports. | Open |
| OQ-04 | P2 | Are Naval Base Kitsap Bremerton and Bangor still BPA direct-service customers? Does PSE serve any federal load as retail? | Defines what KPUD would and would not take over. Federal loads are large. | BPA customer list; Navy (NAVFAC NW) utility contracts; EIA-861 BPA detail. Source S013 is from 2016. | Open |
| OQ-05 | P1 | What is the PSE Kitsap-area peak demand, observed and weather-normalized (1-in-10)? | Peak sets substation, transmission and BPA capacity needs. The module's peak range (342–738 MW) is wide. | PSE's Kitsap non-wires-alternatives RFP; PSE IRP area forecasts; UTC records request; BPA transmission planning. | Open |
| OQ-06 | P1 | How much BPA Tier 1 power could a new Kitsap PUD actually get, and when? KUOW says "200 megawatts" for public utilities. | PSE's "starting with none" claim vs. KUOW's 200 MW. This is the core of the power-supply module. | Ask BPA in writing whether KPUD counts as a "new public" and how much of the limit is left. Price Tier 2 from BPA's rate schedules. | Partly answered 2026-11-05 (S035): new publics share 200 aMW through 2044-09-30, at most 50 aMW per rate period, first come, first served. Eligibility, pool balance and Tier 2 cost are still open. |
| OQ-07 | P2 | Is there any primary source for a $1.2B–$1.5B (or ~$1.5B) Kitsap acquisition value? | Widely repeated, never sourced. A search summary attributed it to a PSE-hired consultant, but S018 and S019 contain no such figure. | Search PSE and campaign materials and PDC filings; ask PSE for the study. Do not use until sourced. | Open |
| OQ-08 | P3 | How much did each side spend on Prop 1? | Context only, not used in the model. | PDC filings (S024, `scripts/fetch_campaign_finance.py`): No committee raised $2,401,233 (PSE $2,318,178, 96.5%) and spent $2,304,528; Yes committee (Unplug PSE) raised $9,055 and spent $7,253. Rerun the script after post-election reports. | Answered 2026-11-04 (filings through Oct 27) |
| OQ-09 | P2 | How many light-duty vehicles are registered in Kitsap? | Turns the EV-stock scenarios into adoption shares, so they can be checked against state ZEV targets. | WA DOL registration counts by county. | Open |
| OQ-10 | P3 | Final certified Prop 1 result. | Status of KPUD's own study: a "No" means KPUD's study "would not move forward" (S002). | `python scripts/fetch_election_results.py` after each count; canvass certifies 2026-11-24 9 a.m. (S005). | Unofficial: No 60.50% (Nov 3, 8:02 PM, 45.1% of registered voters tabulated) |
| OQ-11 | P2 | Jefferson PUD precedent from primary sources: purchase price and adjustments, separation costs, financing, whether voters were asked a second time, rates before and after. | The only modern WA precedent. Current figures come from news coverage (S020). | UTC order approving the PSE sale; Jefferson PUD audited financials; State Auditor reports. | Open |
| OQ-12 | P2 | Kitsap natural-gas therms by sector. | Converts the electrification growth assumption into a derived estimate. | Records request item 5. | Open |
| OQ-13 | P2 | How many Kitsap customers do Peninsula Light and Mason PUD 3 serve? | Separates their load from any county-wide figure. | Ask both utilities (public; PRA applies to Mason PUD 3). | Open |
| OQ-14 | P3 | What did KPUD present to its board (recordings, slides, consultant memos) before placing Prop 1? | May contain load, cost or BPA information already gathered. | Review KPUD "Recordings, Presentations & Board Documents" (S001). | Open |
| OQ-15 | P2 | eGRID cross-check: which eGRID factor produced 219,570 tCO2e? | The NWPP rate implies an impossible PSE factor. The WA-state rate implies ~2.6 TWh. Resolving this would settle Method B. | Records request item 4. | Open |
| OQ-16 | P2 | Would taking over PSE's Kitsap system need a second public vote, and what debt could KPUD's Board issue without one? | Prop 1 did not approve financing, and KPUD promises no second vote: a later decision would be made "by the Board during a public meeting" (S002 p.2). RCW 54.24.018 sends general debt above 3/4 of 1% of taxable value to voters, but its revenue-bond subsection mentions no vote (S026). KPUD's GM is paraphrased as saying an acquisition would likely need a voter-approved bond (S016). | Written answer from KPUD's counsel or a Washington bond attorney. Jefferson PUD's financing record, including whether it held a second vote (OQ-11). Our reading of the statute is not legal advice. | Open |
| OQ-17 | P3 | Can KPUD study electric service without a vote, could it still if "No" holds, and who would pay? | RCW 54.16.010 lets a district make "surveys, plans, investigations or studies" for electric systems, and RCW 54.08.070 requires a vote only to "construct or acquire" (S026). KPUD says asking voters first was its own choice, given the study's cost and past votes elsewhere (S002 p.3). After a "No", "any future action would require a new process" (p.2), and a new authority vote can only be at an even-year general election, so 2028 at the earliest (S026). | Ask KPUD whether anything legally prevents a study after a "No", and which funds could pay for one. | Open |
| OQ-18 | P2 | How much of a new utility's power would be tied to natural gas and carbon prices, and how much of PSE's is? | Whatever BPA Tier 1 doesn't cover (OQ-06) would come from the market or new resources. PSE has this exposure too: 665 MW from Grays Harbor, 700 MW from a converted Centralia, and projected capacity shortfalls of 576 MW in 2026 and 1,404 MW by 2030 (S025). A fair bill comparison (P-6) has to price both sides. | Gas and carbon sensitivities in module 2. PSE's Power Cost Adjustment filings for what reaches bills. The inputs are OQ-20, OQ-21 and OQ-22. | Open |
| OQ-19 | P3 | What would lower Snake River dam removal do to BPA's rates, and could it happen during BPA's post-2028 contracts? | Estimates of replacing the dams' benefits range from $10B to $31B, mostly electricity and grid services (S032). It would affect BPA customers generally, not only a new PUD. Federal policy reversed in June 2025 (S031), a removal plan is still being pushed (S034), and the Army Corps says breaching needs action from Congress (S032). | BPA and Northwest Power and Conservation Council cost analyses. Track litigation and legislation. Treat as a long-term sensitivity in module 2, not a base-case input. | Open |
| OQ-20 | P2 | What were annual average gas prices at Northwest Sumas, 2021–2025? | EIA gives only partial-year figures from licensed data (S030). A public chart's $7.94 for 2022 is unconfirmed. Module 2's gas range needs a full series. | Northwest Power Council staff; PSE's filings in UE-260005 and its resource plan; anyone with licensed data. | Open |
| OQ-21 | P2 | Will the WUTC approve PSE's Centralia tolling agreement, and is the converted plant combined cycle? | It is a 700 MW piece of PSE's plan, and plant type sets the heat rate. S025 says combined cycle; S033 says coal-to-gas. PSE's request is in its rate case (S036), and we found no order. | Watch dockets UE-260005 and UG-260006. Read Exh. BDM-1CT and the public parts of Exh. CJP-25. Check the reported FERC rejection (docket ER26-2422). | Waiting on regulator |
| OQ-22 | P2 | How would a newly serving utility get no-cost carbon allowances, and how many per kWh? | Auction price × emissions may overstate what customers pay (S026, S037). Module 2 has to net allowances out on both sides. | Ecology's 2023–2030 schedule and data set (publication 23-02-031). Ask Ecology in writing about a utility that starts after the schedule was set. | Open |

## PSE's strongest objections, and where this study tests them

Taken from PSE's own release (S018) and quoted coverage (S016). Each one gets a direct, quantified test.
None is dismissed.

| # | Objection (PSE) | Test | Module |
|---|---|---|---|
| P-1 | KPUD has no public plan to fund, operate, maintain or power a ~130,000-customer utility. | This study is that plan's evidence base. Each module must produce numbers with ranges. | all |
| P-2 | KPUD would lose access to cheap federal hydro and would have to buy all its energy, "starting with none." | First result (F-06): a new public starts with no allocation, but BPA's policy lets it add up to 50 aMW per rate period, within a 200 aMW total shared by all new publics (S035). Against ~240 aMW central load, that is about 21% at first and at most 82% later. Still to do: confirm KPUD's eligibility (OQ-06) and price the remainder at Tier 2 or market, with ranges. | 2 |
| P-3 | There would be a "massive cost" to buy PSE's system. Jefferson proponents estimated $47M and the final cost was $109M. | Value Kitsap assets from PSE's FERC Form 1 and UTC rate-base filings. Model condemnation and separation costs. Test how the Jefferson estimate grew, and why, from primary documents (OQ-11). | 3 |
| P-4 | KPUD has no experience running an electric utility this size. | Staffing and O&M benchmarks from utilities of similar size (EIA-861; PUD annual reports). Contract-operations options. | 5 |
| P-5 | Storm response: PSE has 70+ employees and 50+ Potelco contractors (34 line workers) in Kitsap and can draw on crews across the West. | Crew sizing, mutual-aid agreements (WPUDA/NWPPA), and EIA-861 reliability data (SAIDI/SAIFI) for PSE vs. Washington PUDs. | 5 |
| P-6 | Leaving PSE would not lower prices. | Apples-to-apples bill comparison at identical usage, including acquisition debt service and power-supply risk. | 6 |

## Other objections raised in the Prop 1 debate

Raised publicly by Prop 1's opponents, beyond PSE's own release. They get the same treatment.

| # | Objection | Test | Module |
|---|---|---|---|
| D-1 | A feasibility study should come before any vote on authority. | OQ-17 checks whether the law required KPUD's order. It doesn't appear to: KPUD says the order was its own choice (S002 p.3, S026). | all |
| D-2 | Voters would grant authority before knowing the cost, with no second vote promised. | OQ-16 on the vote. Modules 3 and 4 produce the cost range. | 3, 4 |
| D-3 | A public utility still faces clean-energy rules, and public ownership doesn't guarantee lower costs. | Price CETA and carbon for KPUD and PSE alike, then the P-6 bill comparison. | 2, 6 |
| D-4 | Gas and carbon prices could make power expensive (a public chart prices Grays Harbor and Centralia). | Those plants are in PSE's supply, not KPUD's (S025, S002 p.4). The fair version is OQ-18: gas-linked exposure on both sides, using actual carbon prices and only the years they existed. | 2 |
| D-5 | Snake River dam removal could raise BPA's costs. | OQ-19. | 2 |

<!-- BEGIN GENERATED by scripts/build_site.py from docs/gaps.yaml. Edit the .yaml, not this block. -->

## Plans to close the gaps

The same list is on the [project website](https://penpro.github.io/PUD-Feasibility/#unknowns).

### Where the power would come from

#### OQ-06: How much cheap federal hydropower could a new Kitsap utility actually get?

*Status: Partly answered*

**What we know:** BPA's policy opens its lowest-priced (Tier 1) power to new public utilities, with limits: no more than 50 average megawatts added in any two-year rate period, and 200 in total through September 2044. All new utilities share that total, first come, first served. For Kitsap, that would cover about 21% of average use at first and at most about 82% roughly six years later.

**Still unknown:** Whether BPA would count KPUD as a "new public", since BPA's definition says "newly formed" and KPUD already exists. How much of the 200 would be left. What BPA's Tier 2 power and other sellers' power would cost.

**Plan:**

1. Ask BPA in writing whether KPUD would qualify, how much of the limit is left, and the earliest start date. BPA wants a request at least three years before service begins.
2. Ask Jefferson PUD how its 2013 start with BPA worked.
3. Price Tier 1, Tier 2 and market power in Part 2, using BPA's current rate schedules.

**Who:** The study team writes to BPA and Jefferson PUD. People who know BPA contracts can help (D1).

**Closed when:** BPA answers in writing, and Part 2 prices both tiers.

[BPA Provider of Choice Policy](https://bpa.gov/-/media/Aep/power/provider-of-choice/provider-of-choice-policy-march-2024.pdf) · [BPA CHWM Implementation Policy](https://bpa.gov/-/media/Aep/power/provider-of-choice/chwm-implementation-policy-20250814.pdf)

#### OQ-18: How much would bills move with natural gas and carbon prices, at KPUD and at PSE?

*Status: Open*

**What we know:** PSE's supply plan includes 665 MW from Grays Harbor and 700 MW from a converted Centralia plant, and its annual report says power-cost swings are split between PSE and customers on a graduated scale. KPUD has chosen no power source.

**Still unknown:** How much of a new utility's power beyond BPA's limits would depend on gas. How much of PSE's swings reach customers' bills.

**Plan:**

1. Apply the same gas and carbon price ranges to KPUD and PSE in Part 2, using actual auction prices and only the years they existed.
2. Read PSE's Power Cost Adjustment tariff (Schedule 95) and annual reports for the sharing bands.
3. Carry the result into the Part 6 bill comparison.

**Who:** The study team.

**Closed when:** Part 2 shows a range for both sides, and Part 6 uses it.

#### OQ-20: What did natural gas cost at the Northwest Sumas hub each year, including 2022?

*Status: Open*

**What we know:** EIA reports averages of $1.87 per MMBtu for 2024 through October and $1.59 for 2025 through August, both historic lows. A public chart uses $7.94 for 2022, which we could not confirm.

**Still unknown:** Full-year averages. The hub data is licensed, so EIA's articles only give pieces of it.

**Plan:**

1. Ask Northwest Power Council staff for the annual values behind the Sumas price history in its 2023 forecast.
2. Check the gas price assumptions in PSE's rate case (docket UE-260005) and its resource plan.
3. Ask anyone with licensed price data for annual averages only.

**Who:** The study team. Anyone with licensed gas price data can help.

**Closed when:** Annual averages for 2021 through 2025 come from a citable source, with the 2022 figure confirmed or corrected.

[Northwest Power Council 2023 gas price forecast](https://www.nwcouncil.org/fs/18551/2023_12_p2.pdf)

#### OQ-21: Will regulators approve PSE's Centralia gas deal, and what kind of plant will it be?

*Status: Waiting on regulator*

**What we know:** PSE asked the state regulator (WUTC) in its 2026 rate case to find the deal prudent and let it recover the costs from customers. We found no decision yet. PSE's annual report calls the converted plant combined cycle, while TransAlta describes a coal-to-gas conversion.

**Still unknown:** The regulator's decision. The plant's type and heat rate, which set how much gas it burns. Whether a reported federal (FERC) rejection of a related TransAlta tariff changes the deal; we haven't confirmed that report.

**Plan:**

1. Watch WUTC dockets UE-260005 and UG-260006 for the final order.
2. Read PSE's power-cost testimony (Exh. BDM-1CT) and the public parts of its Centralia documents (Exh. CJP-25) for the plant's design.
3. Check FERC docket ER26-2422.

**Who:** The study team. Anyone can watch the docket and tell us when the order lands.

**Closed when:** A WUTC order is on file, and a filing states the plant's type or heat rate.

[PSE testimony in the rate case](https://apiproxy.utc.wa.gov/cases/GetDocument?docID=92&year=2026&docketNumber=260005)

#### OQ-22: How many no-cost carbon allowances would a new utility get?

*Status: Open*

**What we know:** Consumer-owned and investor-owned electric utilities are eligible for no-cost allowances, which state law says are meant to limit the cost to customers. Ecology publishes a schedule through 2030, revised in October 2026.

**Still unknown:** How a utility that starts after the schedule was set would be treated. How much allowances offset carbon costs per kWh.

**Plan:**

1. Work out allowances per kWh for PSE and similar PUDs from Ecology's data set.
2. Ask Ecology in writing how a newly serving utility would enter the schedule.
3. Net the result out of carbon costs in Part 2.

**Who:** The study team.

**Closed when:** Ecology answers in writing, and the per-kWh figures are in Part 2.

[Ecology no-cost allowance page](https://ecology.wa.gov/air-climate/climate-commitment-act/cap-and-invest/no-cost-allowances)

#### OQ-19: What would removing the lower Snake River dams do to BPA's rates?

*Status: Open*

**What we know:** Estimates of replacing the dams' benefits range from $10 billion to $31 billion, mostly electricity and grid services. The Army Corps doesn't consider itself free to breach them without action from Congress, and we found no sign of that.

**Still unknown:** What removal would mean for BPA's rates, and when, if it ever happens.

**Plan:**

1. Read the August 2022 Benefit Replacement Report and the studies it draws on.
2. Turn the range into a BPA rate effect in Part 2, labeled as a long-term sensitivity.
3. Track the federal lawsuit and any legislation.

**Who:** The study team.

**Closed when:** Part 2 shows a sourced rate range.

[Congressional Research Service report](https://www.everycrsreport.com/files/2026-07-31_R48089_bad001768c585fb5797f80ad80ecc088f185947b.html)

### What the law and KPUD would require

#### OQ-16: Would a takeover need a second public vote?

*Status: Open*

**What we know:** Prop 1 did not approve financing, and KPUD promises no second vote. State law sends some general debt to voters, but its revenue-bond section mentions no vote. KUOW paraphrased KPUD's general manager as saying a takeover would likely need a voter-approved bond.

**Still unknown:** Whether a takeover paid for with revenue bonds would need a public vote. Our reading of the statute is not legal advice.

**Plan:**

1. Ask KPUD in writing how it reads RCW 54.24.018 for a takeover.
2. Check how other Washington PUDs sold electric revenue bonds, using their bond documents on EMMA.
3. Have a Washington municipal finance lawyer check our reading (D6).

**Who:** The study team writes to KPUD. This needs a lawyer's help (D6).

**Closed when:** KPUD's lawyers or a bond attorney answer in writing, with citations.

[RCW 54.24.018](https://app.leg.wa.gov/RCW/default.aspx?cite=54.24.018)

#### OQ-17: Could KPUD study this without a vote, and who would pay?

*Status: Open*

**What we know:** State law lets a PUD make studies for electric systems and requires a vote only to build or buy. KPUD says voting first was its own choice, because of the study's cost and past votes elsewhere. A new vote on authority couldn't happen before the 2028 general election.

**Still unknown:** Whether anything stops KPUD from studying after a "No". What money could pay for it; KPUD's fact sheet doesn't say how the study would be funded.

**Plan:**

1. Ask KPUD both questions in writing.
2. Review KPUD's board recordings and slides from before Prop 1 (OQ-14).

**Who:** The study team.

**Closed when:** KPUD answers in writing.

[RCW 54.16.010](https://app.leg.wa.gov/RCW/default.aspx?cite=54.16.010) · [RCW 54.08.070](https://app.leg.wa.gov/RCW/default.aspx?cite=54.08.070)

### What a takeover would cost

#### OQ-07: What would it cost to buy PSE's Kitsap equipment?

*Status: Open*

**What we know:** A $1.2–1.5 billion figure keeps getting repeated, but we have found no original source for it. PSE's own release gives no Kitsap estimate.

**Still unknown:** The actual value, and what it would cost to separate Kitsap from PSE's system.

**Plan:**

1. Trace where the repeated figure came from (A1).
2. Value Kitsap's equipment from PSE's federal and state filings in Part 3.
3. Model a court-set price and separation costs, tested against Jefferson County's experience.

**Who:** Anyone can help trace the figure (A1). The study team builds Part 3.

**Closed when:** The figure is sourced or retired, and Part 3 publishes a range.

#### OQ-11: How was Jefferson PUD's takeover paid for, and was there a second vote?

*Status: Open*

**What we know:** News coverage reports a $103 million agreement that rose to about $109 million, with most of the money from a federal USDA loan, after a 2008 vote gave the PUD authority.

**Still unknown:** The final loan and bond terms, the separation costs, and whether voters were asked again. We have found no record of a second vote, but we haven't ruled one out.

**Plan:**

1. Pull the WUTC order, Jefferson PUD's audited statements (State Auditor) and its bond documents (EMMA).
2. Check the Jefferson County Auditor's election records from 2009 through 2013 for any PUD bond measure.
3. Ask Jefferson PUD directly. State public records law applies.

**Who:** Records help is wanted (C4).

**Closed when:** Primary documents show the financing, and election records show whether a second vote happened.

### How much electricity Kitsap uses

#### OQ-01, OQ-02: How much electricity does Kitsap actually use, measured rather than estimated?

*Status: Requests sent*

**What we know:** Our estimate is about 2.04 TWh a year (range 1.74–2.60), built from indirect data.

**Still unknown:** The measured kWh behind the county's 2022 greenhouse gas inventory, by sector, and which emission factor it used.

**Plan:**

1. Records requests went to Commerce and Kitsap County on Nov 4, 2026, 2:30 PM. First replies are due by Thu, Nov 12.
2. Log each reply on this site and follow up on any delay.
3. Replace the back-calculation with the measured numbers.

**Who:** The study team, waiting on the two agencies.

**Closed when:** Measured kWh by sector is on file and in the model.

#### OQ-03: How many PSE customers are in Kitsap, by type?

*Status: Open*

**What we know:** PSE says about 130,000. That number is rounded and comes from PSE's own press release.

**Still unknown:** The exact count, split between homes and businesses.

**Plan:**

1. Check PSE's filings with the state regulator and its community reports.
2. Ask PSE directly.
3. If neither gives the count, file a records request with the regulator.

**Who:** The study team. Records help is welcome (C5).

**Closed when:** A filed or agency count by customer type is in the model.

#### OQ-05: What is Kitsap's actual peak demand?

*Status: Open*

**What we know:** Our range is 342–738 MW, taken from neighboring utilities' patterns rather than Kitsap measurements. Peak demand sets how much equipment and transmission a utility needs.

**Still unknown:** The measured Kitsap peak, and what a severe winter would do to it.

**Plan:**

1. Read PSE's Kitsap non-wires-alternatives request for proposals and its area load forecasts.
2. Ask the state regulator for area load data through a records request.
3. Check BPA's transmission planning documents.

**Who:** The study team. Records help is welcome (C1).

**Closed when:** A measured or filed Kitsap-area peak, adjusted for weather, is in the model.

<!-- END GENERATED -->
