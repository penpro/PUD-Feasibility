"""Module 1, Load: how much energy and peak demand would a KPUD electric utility serve?

Scope: PSE's retail load inside Kitsap County, the system KPUD would acquire. Excludes BPA
direct-service federal load (Naval Base Kitsap Bremerton and Bangor, S013) and the parts of the
county served by Peninsula Light and Mason PUD 3 (S010).

Annual energy, three independent approaches:
  A  FindEnergy county figure (third-party): tested for circularity, NOT used
  B  2022 GHG-inventory electricity emissions / PSE carbon intensity -> kWh
  C  bottom-up: PSE Kitsap customers x class mix x per-customer use (EIA-861 2025)

    python -m model.load        # writes data/processed/load/*.csv and modules/01_load/results.md
"""
from __future__ import annotations

import itertools
from pathlib import Path

import pandas as pd

from . import eia861
from .common import (CASES, HOURS_PER_YEAR, PROCESSED, ROOT, g_per_mj_to_t_per_mwh,
                     load_config, param, ref, val)

OUT = PROCESSED / "load"
RESULTS_MD = ROOT / "modules" / "01_load" / "results.md"
MONTHLY_YEARS = (2022, 2023, 2024, 2025)
INVENTORY_YEAR = 2022


# ---------------------------------------------------------------- helpers
def population(cfg: dict, year: float) -> float:
    """Geometric interpolation/extrapolation of the OFM projection points."""
    pts = sorted((int(k), float(v)) for k, v in param(cfg, "load.population_projection")["points"].items())
    segs = list(zip(pts, pts[1:]))
    for (y0, p0), (y1, p1) in segs:
        if y0 <= year <= y1:
            break
    else:
        (y0, p0), (y1, p1) = segs[0] if year < pts[0][0] else segs[-1]
    rate = (p1 / p0) ** (1 / (y1 - y0))
    return p0 * rate ** (year - y0)


def twh(mwh: float) -> str:
    return f"{mwh / 1e6:.2f}"


def num(x: float) -> str:
    return f"{x:,.0f}" if float(x).is_integer() else f"{x:,}"


def mw(x: float) -> str:
    return f"{x:,.0f}"


# ---------------------------------------------------------------- method A
def method_a(cfg: dict) -> dict:
    k = "load.findenergy_claim"
    total = val(cfg, f"{k}.kitsap_total_mwh")
    popn = val(cfg, f"{k}.kitsap_population")
    state_pc = val(cfg, f"{k}.wa_per_capita_mwh")
    implied_pc = total / popn
    return {
        "total_mwh": total,
        "avg_mw": total / HOURS_PER_YEAR,
        "implied_per_capita_mwh": implied_pc,
        "state_per_capita_mwh": state_pc,
        "state_pc_x_county_pop_mwh": state_pc * popn,
        "is_state_average_scaled": abs(implied_pc - state_pc) < 0.01,
    }


# ---------------------------------------------------------------- method B
LB_PER_TONNE = 2204.62
# Every PSE factor the inventory could plausibly have used: fuel-mix year x CI component.
EF_MATRIX = (
    (2021, "lifecycle total", "ci_2021mix_total"),
    (2021, "production-to-consumption", "ci_2021mix_production_to_consumption"),
    (2022, "lifecycle total", "ci_2022mix_total"),
    (2022, "production-to-consumption", "ci_2022mix_production_to_consumption"),
    (2023, "lifecycle total", "ci_2023mix_total"),
    (2023, "production-to-consumption", "ci_2023mix_production_to_consumption"),
)


def method_b_matrix(cfg: dict) -> pd.DataFrame:
    total_t = val(cfg, "load.ghg_inventory_2022.electricity_total")
    loc_t = val(cfg, "load.ghg_inventory_2022.electricity_location_based")
    rows = []
    for year, component, key in EF_MATRIX:
        ef = val(cfg, f"load.pse_carbon_intensity.{key}")
        mwh = total_t / g_per_mj_to_t_per_mwh(ef)
        rows.append({"fuel_mix_year": year, "component": component, "ef_gco2e_per_mj": ef,
                     "total_mwh_2022": mwh, "implied_location_factor_lb_per_mwh": loc_t / mwh * LB_PER_TONNE})
    return pd.DataFrame(rows)


def egrid_check(cfg: dict) -> pd.DataFrame:
    """kWh implied by the inventory's location-based figure under each published eGRID rate."""
    loc_t = val(cfg, "load.ghg_inventory_2022.electricity_location_based")
    total_t = val(cfg, "load.ghg_inventory_2022.electricity_total")
    nwpp = val(cfg, "load.egrid2022.nwpp_co2e_lb_per_mwh")
    wa = val(cfg, "load.egrid2022.wa_state_co2e_lb_per_mwh")
    loss = val(cfg, "load.egrid2022.nwpp_grid_gross_loss")
    rows = []
    for name, rate in (("NWPP subregion", nwpp), ("NWPP incl. grid gross loss", nwpp / (1 - loss)),
                       ("Washington state", wa), ("Washington state incl. NWPP gross loss", wa / (1 - loss))):
        mwh = loc_t / (rate / LB_PER_TONNE)
        rows.append({"egrid_basis": name, "rate_lb_per_mwh": rate, "implied_total_mwh": mwh,
                     "pse_factor_this_would_require_gco2e_per_mj": total_t / mwh / 0.0036})
    return pd.DataFrame(rows)


def method_b(cfg: dict) -> pd.DataFrame:
    g = "load.ghg_inventory_2022"
    e = {s: val(cfg, f"{g}.electricity_{s}") for s in ("residential", "commercial", "industrial", "total")}
    assert e["residential"] + e["commercial"] + e["industrial"] == e["total"], "inventory sectors must sum"
    scale = population(cfg, cfg["settings"]["base_year"]) / population(cfg, INVENTORY_YEAR)
    rows = []
    # A higher emission factor implies LESS energy, so the high EF is the low-load case.
    for load_case, ef_case in (("low", "high"), ("central", "central"), ("high", "low")):
        ef_g = val(cfg, "load.ghg_backcalc_ef", ef_case)
        ef_t = g_per_mj_to_t_per_mwh(ef_g)
        res, com, ind = (e[s] / ef_t for s in ("residential", "commercial", "industrial"))
        total = res + com + ind
        rows.append({
            "load_case": load_case, "ef_gco2e_per_mj": ef_g, "ef_tco2e_per_mwh": ef_t,
            "residential_mwh": res, "commercial_mwh": com, "industrial_mwh": ind,
            "total_mwh_2022": total, "pop_scale_2022_to_base": scale,
            "total_mwh_base": total * scale, "avg_mw_base": total * scale / HOURS_PER_YEAR,
            "implied_location_factor_lb_per_mwh":
                val(cfg, f"{g}.electricity_location_based") / total * LB_PER_TONNE,
        })
    return pd.DataFrame(rows).set_index("load_case")


# ---------------------------------------------------------------- method C
C_PARAMS = ("pse_kitsap_customers", "residential_customer_share",
            "residential_mwh_per_customer", "commercial_mwh_per_customer")


def bottom_up(cfg: dict, values: dict[str, float]) -> dict:
    n = values["pse_kitsap_customers"]
    share = values["residential_customer_share"]
    res_n, com_n = n * share, n * (1 - share)
    res = res_n * values["residential_mwh_per_customer"]
    com = com_n * values["commercial_mwh_per_customer"]
    ind = (res + com) * val(cfg, "load.bottom_up.industrial_uplift")
    return {"residential_customers": res_n, "commercial_customers": com_n,
            "residential_mwh": res, "commercial_mwh": com, "industrial_mwh": ind,
            "total_mwh": res + com + ind}


def method_c(cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    def pv(name: str, case: str) -> float:
        return val(cfg, f"load.bottom_up.{name}", case)

    central_vals = {p: pv(p, "central") for p in C_PARAMS}
    corners = []
    for combo in itertools.product(("low", "high"), repeat=len(C_PARAMS)):
        v = {p: pv(p, c) for p, c in zip(C_PARAMS, combo)}
        corners.append((bottom_up(cfg, v)["total_mwh"], combo))
    lo, hi = min(corners), max(corners)
    rows = {}
    for case, vals_ in (("low", dict(zip(C_PARAMS, (pv(p, c) for p, c in zip(C_PARAMS, lo[1]))))),
                        ("central", central_vals),
                        ("high", dict(zip(C_PARAMS, (pv(p, c) for p, c in zip(C_PARAMS, hi[1])))))):
        r = bottom_up(cfg, vals_)
        r.update({f"in_{k}": v for k, v in vals_.items()})
        r["avg_mw"] = r["total_mwh"] / HOURS_PER_YEAR
        rows[case] = r
    cases = pd.DataFrame(rows).T
    cases.index.name = "load_case"

    base = bottom_up(cfg, central_vals)["total_mwh"]
    tor = []
    for p in C_PARAMS:
        out = {}
        for c in ("low", "high"):
            v = dict(central_vals)
            v[p] = pv(p, c)
            out[c] = bottom_up(cfg, v)["total_mwh"]
        tor.append({"parameter": p, "param_low": pv(p, "low"), "param_high": pv(p, "high"),
                    "total_mwh_at_param_low": out["low"], "total_mwh_at_param_high": out["high"],
                    "swing_mwh": abs(out["high"] - out["low"]), "swing_pct_of_central": abs(out["high"] - out["low"]) / base})
    tornado = pd.DataFrame(tor).sort_values("swing_mwh", ascending=False).set_index("parameter")
    return cases, tornado


# ---------------------------------------------------------------- reconcile, peak
def reconcile(b: pd.DataFrame, c: pd.DataFrame) -> pd.DataFrame:
    central = (b.loc["central", "total_mwh_base"] + c.loc["central", "total_mwh"]) / 2
    rows = {
        "low": {"retail_mwh": b.loc["low", "total_mwh_base"], "basis": "B low (largest PSE factor: 2021 mix, lifecycle), population-scaled"},
        "central": {"retail_mwh": central, "basis": "mean of B central and C central"},
        "high": {"retail_mwh": b.loc["high", "total_mwh_base"], "basis": "B high (smallest PSE factor: 2023 mix, production-to-consumption), population-scaled"},
        "stress_low": {"retail_mwh": c.loc["low", "total_mwh"], "basis": "C, every input at its low-load end"},
        "stress_high": {"retail_mwh": c.loc["high", "total_mwh"], "basis": "C, every input at its high-load end"},
    }
    df = pd.DataFrame(rows).T
    df["retail_mwh"] = df["retail_mwh"].astype(float)
    df["avg_mw_at_meter"] = df["retail_mwh"] / HOURS_PER_YEAR
    df.index.name = "case"
    return df


# Low-load case pairs with low losses and a HIGH load factor (low peak), and vice versa.
PEAK_PAIRING = {"low": ("low", "high"), "central": ("central", "central"), "high": ("high", "low")}


def peak_case(cfg: dict, retail_mwh: float, case: str) -> dict:
    loss_case, lf_case = PEAK_PAIRING[case]
    loss = val(cfg, "load.losses", loss_case)
    lf = val(cfg, "load.load_factor", lf_case)
    system_mwh = retail_mwh / (1 - loss)
    avg = system_mwh / HOURS_PER_YEAR
    return {"retail_mwh": retail_mwh, "loss_fraction": loss, "system_input_mwh": system_mwh,
            "avg_mw_system": avg, "load_factor": lf, "peak_mw": avg / lf}


def peaks(cfg: dict, recon: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame({c: peak_case(cfg, recon.loc[c, "retail_mwh"], c) for c in CASES}).T
    df.index.name = "case"
    return df


# ---------------------------------------------------------------- monthly shape
def monthly_shares() -> pd.DataFrame:
    frames = []
    for y in MONTHLY_YEARS:
        m = eia861.monthly_sales(y).set_index("Month")
        if len(m) != 12:
            raise ValueError(f"PSE 861M {y}: expected 12 months, got {len(m)}")
        frames.append(pd.DataFrame({
            cls: m[f"{cls.upper()}|Sales"] / m[f"{cls.upper()}|Sales"].sum()
            for cls in ("residential", "commercial", "industrial")
        }).assign(year=y))
    allyrs = pd.concat(frames)
    shares = allyrs.groupby(level=0)[["residential", "commercial", "industrial"]].mean()
    shares.index.name = "month"
    return shares


def monthly(c_central: pd.Series, recon_central: float) -> pd.DataFrame:
    shares = monthly_shares()
    # Scale the bottom-up class mix to the reconciled central total.
    k = recon_central / c_central["total_mwh"]
    annual = {cls: c_central[f"{cls}_mwh"] * k for cls in ("residential", "commercial", "industrial")}
    df = pd.DataFrame({f"{cls}_mwh": shares[cls] * annual[cls] for cls in annual})
    df["total_mwh"] = df.sum(axis=1)
    hours = pd.Series([pd.Period(f"2025-{m:02d}").days_in_month * 24 for m in df.index], index=df.index)
    df["hours"] = hours
    df["avg_mw_at_meter"] = df["total_mwh"] / hours
    df["ratio_to_annual_avg"] = df["avg_mw_at_meter"] / (recon_central / HOURS_PER_YEAR)
    for cls in annual:
        df[f"{cls}_share"] = shares[cls]
    return df


# ---------------------------------------------------------------- projections
def ev_stock(cfg: dict, year: int, case: str) -> float:
    e26 = val(cfg, "load.growth.ev_stock_2026")
    e35 = val(cfg, "load.growth.ev_stock_2035", case)
    e45 = val(cfg, "load.growth.ev_stock_2045", case)
    if year <= 2026:
        return e26
    if year <= 2035:
        return e26 + (e35 - e26) * (year - 2026) / (2035 - 2026)
    return e35 + (e45 - e35) * (year - 2035) / (2045 - 2035)


def projections(cfg: dict, recon: pd.DataFrame) -> pd.DataFrame:
    base_year = cfg["settings"]["base_year"]
    rows = []
    for case in CASES:
        base = recon.loc[case, "retail_mwh"]
        change = val(cfg, "load.growth.per_customer_change_by_2045", case)
        kwh_ev = val(cfg, "load.growth.kwh_per_ev_year", case)
        e26 = val(cfg, "load.growth.ev_stock_2026")
        for y in cfg["settings"]["projection_years"]:
            pop_ratio = population(cfg, y) / population(cfg, base_year)
            f = 1 + change * (y - base_year) / (2045 - base_year)
            non_ev = base * pop_ratio * f
            evs = ev_stock(cfg, y, case)
            ev_mwh = max(0.0, evs - e26) * kwh_ev / 1000
            total = non_ev + ev_mwh
            pk = peak_case(cfg, total, case)
            rows.append({"case": case, "year": y, "population": population(cfg, y),
                         "non_ev_mwh": non_ev, "ev_stock": evs, "ev_adder_mwh": ev_mwh,
                         "retail_mwh": total, "avg_mw_at_meter": total / HOURS_PER_YEAR,
                         "peak_mw": pk["peak_mw"]})
    return pd.DataFrame(rows).set_index(["case", "year"])


# ---------------------------------------------------------------- report
def provenance_table(cfg: dict, keys: list[str]) -> list[str]:
    lines = ["| Parameter | Value(s) | Unit | Label · Source | As of |", "|---|---|---|---|---|"]
    for k in keys:
        p = param(cfg, k)
        if "value" in p:
            v = f"{p['value']:,}" if isinstance(p["value"], (int, float)) else str(p["value"])
        elif "points" in p:
            v = "; ".join(f"{y}: {n:,}" for y, n in p["points"].items())
        else:
            v = " / ".join(f"{p[c]:,}" for c in CASES) + " (low/central/high)"
        lines.append(f"| `{k.removeprefix('load.')}` | {v} | {p['unit']} | {ref(cfg, k)} | {p['as_of']} |")
    return lines


def write_results(cfg, a, b, bm, eg, c, tornado, recon, pk, mon, proj) -> str:
    base_year = cfg["settings"]["base_year"]
    kuow = val(cfg, "load.kuow_claim_mw")
    L: list[str] = []
    w = L.append
    w("# Module 1, Load: results")
    w("")
    w(f"<!-- GENERATED by `python -m model.load` (study v{cfg['meta']['study_version']}, config as of "
      f"{cfg['meta']['config_as_of']}). Do not edit by hand; change model/config.yaml and rerun. -->")
    w("")
    w("**Status: preliminary (v0).** Scope is PSE's retail load in Kitsap County, the system KPUD would "
      "acquire. Every input is labeled; see the provenance table at the end. All values are ESTIMATES "
      "unless stated otherwise.")
    w("")
    w("## Headline")
    w("")
    w(f"| Quantity ({base_year}) | Low | Central | High | Stress range |")
    w("|---|---|---|---|---|")
    w(f"| Annual retail energy (TWh) | {twh(recon.loc['low','retail_mwh'])} | {twh(recon.loc['central','retail_mwh'])} | "
      f"{twh(recon.loc['high','retail_mwh'])} | {twh(recon.loc['stress_low','retail_mwh'])}–{twh(recon.loc['stress_high','retail_mwh'])} |")
    w(f"| Average load at meter (MW) | {mw(recon.loc['low','avg_mw_at_meter'])} | {mw(recon.loc['central','avg_mw_at_meter'])} | "
      f"{mw(recon.loc['high','avg_mw_at_meter'])} | {mw(recon.loc['stress_low','avg_mw_at_meter'])}–{mw(recon.loc['stress_high','avg_mw_at_meter'])} |")
    w(f"| Average load incl. losses (MW) | {mw(pk.loc['low','avg_mw_system'])} | {mw(pk.loc['central','avg_mw_system'])} | {mw(pk.loc['high','avg_mw_system'])} | |")
    w(f"| Annual peak (MW) | {mw(pk.loc['low','peak_mw'])} | {mw(pk.loc['central','peak_mw'])} | {mw(pk.loc['high','peak_mw'])} | |")
    w("")
    ratio = a["total_mwh"] / recon.loc["central", "retail_mwh"]
    over_hi = a["total_mwh"] / recon.loc["stress_high", "retail_mwh"] - 1
    w(f"- FindEnergy's **3.24 TWh** (and the ~370 MW average it implies) is not a measurement of Kitsap. It is Washington's "
      f"statewide per-capita use ({a['state_per_capita_mwh']} MWh) times county population (Method A). It is **{ratio:.2f}x** "
      f"this module's central estimate and {over_hi:.0%} above even the stress-high case.")
    w(f"- KUOW's \"around {kuow:.0f} megawatts\" (UNVERIFIED, S016) does not say average or peak. As an **average** it is "
      f"{kuow / recon.loc['central','avg_mw_at_meter']:.2f}x the central estimate and above even the stress-high case. As a **peak** "
      f"it falls inside this module's peak range ({mw(pk.loc['low','peak_mw'])}–{mw(pk.loc['high','peak_mw'])} MW). "
      "It fits a peak figure. It does not fit average energy.")
    w("- Peak demand is the least certain number here. It drives substation, transmission and BPA capacity costs, "
      "so PSE's Kitsap-area peak data is the top data request (OQ-05).")
    w("")
    w("## Method A: FindEnergy county figure (tested, not used)")
    w("")
    w(f"- FindEnergy Kitsap: {a['total_mwh']:,.0f} MWh / population {val(cfg, 'load.findenergy_claim.kitsap_population'):,.0f} "
      f"= **{a['implied_per_capita_mwh']:.3f} MWh per person**.")
    w(f"- FindEnergy Washington statewide: **{a['state_per_capita_mwh']} MWh per person** "
      f"({val(cfg, 'load.findenergy_claim.wa_total_mwh'):,.0f} MWh). The same value appears on the Kittitas and Jefferson pages (S014).")
    w(f"- Statewide per-capita x Kitsap population = {a['state_pc_x_county_pop_mwh']:,.0f} MWh, matching the published figure. "
      f"Verdict: **{'statewide average scaled by population' if a['is_state_average_scaled'] else 'not a simple scaling'}**. "
      "The statewide average includes data-center, pulp-and-paper and irrigation loads Kitsap does not have. Even a "
      "correct county total would also include BPA's federal direct-service load (S013) and Peninsula Light and Mason PUD 3 "
      "customers, none of which KPUD would acquire from PSE.")
    w("")
    w("## Method B: back-calculated from the 2022 county GHG inventory")
    w("")
    w("kWh = (electricity tCO2e, S006) / (PSE carbon intensity, S007–S009). The inventory publishes emissions, not kWh, "
      "and does not say which PSE factor it used. Every plausible factor:")
    w("")
    w("| Fuel-mix year | CI component | PSE factor (gCO2e/MJ) | Implied 2022 total (TWh) | Implied location-based factor (lb/MWh) |")
    w("|---|---|---|---|---|")
    for _, r in bm.iterrows():
        w(f"| {r.fuel_mix_year} | {r.component} | {r.ef_gco2e_per_mj} | {twh(r.total_mwh_2022)} | {r.implied_location_factor_lb_per_mwh:,.0f} |")
    w("")
    w("Cases used (low/high = the largest/smallest factor in the matrix; central = 2022 mix, production-to-consumption. "
      "It matches the inventory year, it is the component that includes T&D, and community inventories normally exclude upstream emissions):")
    w("")
    w("| Load case | PSE factor (gCO2e/MJ) | tCO2e/MWh | Residential (MWh) | Commercial (MWh) | Industrial (MWh) | Total 2022 (TWh) | "
      f"Total {base_year} pop-scaled (TWh) |")
    w("|---|---|---|---|---|---|---|---|")
    for case, r in b.iterrows():
        w(f"| {case} | {r.ef_gco2e_per_mj} | {r.ef_tco2e_per_mwh:.4f} | {r.residential_mwh:,.0f} | {r.commercial_mwh:,.0f} | "
          f"{r.industrial_mwh:,.0f} | {twh(r.total_mwh_2022)} | {twh(r.total_mwh_base)} |")
    w("")
    w(f"- Sector split (all cases): residential {b.loc['central','residential_mwh']/b.loc['central','total_mwh_2022']:.1%}, "
      f"commercial {b.loc['central','commercial_mwh']/b.loc['central','total_mwh_2022']:.1%}, industrial "
      f"{b.loc['central','industrial_mwh']/b.loc['central','total_mwh_2022']:.1%}. This holds only if one emission factor was "
      "applied to every sector (OQ-02).")
    w(f"- Population scaling 2022 to {base_year}: x{b.loc['central','pop_scale_2022_to_base']:.4f} (OFM, S006), with per-customer use held flat.")
    w("")
    w("**eGRID cross-check.** The inventory also reports a location-based figure (219,570 tCO2e) using an unnamed \"regional\" "
      "eGRID factor. Dividing by each published eGRID2022 rate (S023):")
    w("")
    w("| eGRID basis | Rate (lb CO2e/MWh) | Implied total (TWh) | PSE factor that total would require (gCO2e/MJ) |")
    w("|---|---|---|---|")
    for _, r in eg.iterrows():
        w(f"| {r.egrid_basis} | {r.rate_lb_per_mwh:,.1f} | {twh(r.implied_total_mwh)} | {r.pse_factor_this_would_require_gco2e_per_mj:,.1f} |")
    w("")
    w("- The NWPP subregion rate implies a PSE factor about twice anything Ecology has published for PSE (90–135), so the "
      "inventory probably did not apply NWPP to the same kWh.")
    w("- The Washington state rate implies ~2.5–2.6 TWh, near the top of the matrix (2023-mix production-to-consumption). "
      "The check leans toward the upper half of Method B's range but cannot settle it. The consultant's actual factors are "
      "records request item 4.")
    w("")
    w(f"## Method C: bottom-up from customers and EIA-861 {eia861.ANNUAL_YEAR} benchmarks")
    w("")
    w("| Case | Customers | Residential share | Res. MWh/cust | Com. MWh/cust | Residential (MWh) | Commercial (MWh) | Total (TWh) | Avg MW |")
    w("|---|---|---|---|---|---|---|---|---|")
    for case, r in c.iterrows():
        w(f"| {case} | {r.in_pse_kitsap_customers:,.0f} | {r.in_residential_customer_share:.2f} | {r.in_residential_mwh_per_customer:.2f} | "
          f"{r.in_commercial_mwh_per_customer:.2f} | {r.residential_mwh:,.0f} | {r.commercial_mwh:,.0f} | {twh(r.total_mwh)} | {mw(r.avg_mw)} |")
    w("")
    w("Low and high are the corner combinations giving the minimum and maximum total (every input at its worst end at once), so this is a deliberately wide stress range.")
    w("")
    w("**One-at-a-time sensitivity (others at central):**")
    w("")
    w("| Parameter | Param low → high | Total at low (TWh) | Total at high (TWh) | Swing (% of central) |")
    w("|---|---|---|---|---|")
    for p, r in tornado.iterrows():
        w(f"| `{p}` | {num(r.param_low)} → {num(r.param_high)} | {twh(r.total_mwh_at_param_low)} | {twh(r.total_mwh_at_param_high)} | {r.swing_pct_of_central:.0%} |")
    w("")
    gap = c.loc["central", "total_mwh"] / b.loc["central", "total_mwh_base"] - 1
    w(f"- Method C central ({twh(c.loc['central','total_mwh'])} TWh) is {gap:+.1%} from Method B central "
      f"({twh(b.loc['central','total_mwh_base'])} TWh). The two share no inputs except the <1% industrial uplift. "
      "Method B's whole range sits inside Method C's stress range.")
    w("")
    w("## Reconciled estimate")
    w("")
    w("| Case | Retail energy (TWh) | Avg MW at meter | Basis |")
    w("|---|---|---|---|")
    for case, r in recon.iterrows():
        w(f"| {case} | {twh(r.retail_mwh)} | {mw(r.avg_mw_at_meter)} | {r.basis} |")
    w("")
    w("## Peak demand")
    w("")
    w("Peak = retail / (1 − loss fraction) / 8,760 / load factor. Low-load cases pair with low losses and a high load "
      "factor, and high-load cases with the reverse.")
    w("")
    w("| Case | Retail (TWh) | Loss fraction | Avg MW incl. losses | Load factor | Peak (MW) |")
    w("|---|---|---|---|---|---|")
    for case, r in pk.iterrows():
        w(f"| {case} | {twh(r.retail_mwh)} | {r.loss_fraction:.4f} | {mw(r.avg_mw_system)} | {r.load_factor:.4f} | {mw(r.peak_mw)} |")
    w("")
    w("Load factors are from 2025 observed peaks (EIA-861), not 1-in-10 cold-weather design peaks. A planning peak "
      "would be higher.")
    w("")
    w("## Monthly shape (central case)")
    w("")
    w(f"Class shares are PSE system-wide billed sales averaged over {MONTHLY_YEARS[0]}–{MONTHLY_YEARS[-1]} (EIA-861M, S011). "
      "Billing lag shifts the shape by roughly half a month. Kitsap probably peaks harder in winter than PSE's system "
      "as a whole, since more of its homes heat with electricity.")
    w("")
    w("| Month | Residential (MWh) | Commercial (MWh) | Total (MWh) | Avg MW | x annual avg |")
    w("|---|---|---|---|---|---|")
    for m, r in mon.iterrows():
        w(f"| {m} | {r.residential_mwh:,.0f} | {r.commercial_mwh:,.0f} | {r.total_mwh:,.0f} | {mw(r.avg_mw_at_meter)} | {r.ratio_to_annual_avg:.2f} |")
    w("")
    w("## Projections")
    w("")
    w("Customers grow with the OFM population projection. Per-customer use changes linearly to its 2045 value. EV "
      "energy is added above the 2026 registered fleet. The load factor is held constant, which is a simplification: "
      "heat pumps raise winter peaks and managed EV charging can lower them.")
    w("")
    w("| Year | Low (TWh) | Central (TWh) | High (TWh) | Central EV adder (TWh) | Peak low (MW) | Peak central (MW) | Peak high (MW) |")
    w("|---|---|---|---|---|---|---|---|")
    for y in cfg["settings"]["projection_years"]:
        lo, ce, hi = (proj.loc[(c_, y)] for c_ in CASES)
        w(f"| {y} | {twh(lo.retail_mwh)} | {twh(ce.retail_mwh)} | {twh(hi.retail_mwh)} | {twh(ce.ev_adder_mwh)} | "
          f"{mw(lo.peak_mw)} | {mw(ce.peak_mw)} | {mw(hi.peak_mw)} |")
    w("")
    w("## Inputs and provenance")
    w("")
    keys = ["load.ghg_inventory_2022.electricity_total", "load.ghg_inventory_2022.electricity_residential",
            "load.ghg_inventory_2022.electricity_commercial", "load.ghg_inventory_2022.electricity_industrial",
            "load.ghg_inventory_2022.electricity_location_based",
            "load.pse_carbon_intensity.ci_2021mix_total", "load.pse_carbon_intensity.ci_2021mix_production_to_consumption",
            "load.pse_carbon_intensity.ci_2022mix_total", "load.pse_carbon_intensity.ci_2022mix_production_to_consumption",
            "load.pse_carbon_intensity.ci_2023mix_total", "load.pse_carbon_intensity.ci_2023mix_production_to_consumption",
            "load.ghg_backcalc_ef", "load.egrid2022.nwpp_co2e_lb_per_mwh", "load.egrid2022.wa_state_co2e_lb_per_mwh",
            "load.egrid2022.nwpp_grid_gross_loss",
            "load.findenergy_claim.kitsap_total_mwh", "load.findenergy_claim.wa_per_capita_mwh", "load.kuow_claim_mw",
            "load.bottom_up.pse_kitsap_customers", "load.bottom_up.residential_customer_share",
            "load.bottom_up.residential_mwh_per_customer", "load.bottom_up.commercial_mwh_per_customer",
            "load.bottom_up.industrial_uplift", "load.losses", "load.load_factor", "load.population_projection",
            "load.growth.per_customer_change_by_2045", "load.growth.ev_stock_2026", "load.growth.ev_stock_2035",
            "load.growth.ev_stock_2045", "load.growth.kwh_per_ev_year"]
    L.extend(provenance_table(cfg, keys))
    w("")
    w("CSV outputs: `data/processed/load/`. Benchmarks: `data/processed/eia861_2025_benchmarks.csv`.")
    w("")
    return "\n".join(L)


def run() -> dict:
    cfg = load_config()
    OUT.mkdir(parents=True, exist_ok=True)
    a = method_a(cfg)
    b = method_b(cfg)
    bm = method_b_matrix(cfg)
    eg = egrid_check(cfg)
    c, tornado = method_c(cfg)
    recon = reconcile(b, c)
    pk = peaks(cfg, recon)
    mon = monthly(c.loc["central"], recon.loc["central", "retail_mwh"])
    proj = projections(cfg, recon)

    eia861.benchmarks().round(4).to_csv(PROCESSED / "eia861_2025_benchmarks.csv")
    pd.Series(a).to_frame("value").to_csv(OUT / "method_a_findenergy_test.csv")
    b.round(4).to_csv(OUT / "method_b_ghg_backcalc.csv")
    bm.round(4).to_csv(OUT / "method_b_factor_matrix.csv", index=False)
    eg.round(4).to_csv(OUT / "method_b_egrid_check.csv", index=False)
    c.round(4).to_csv(OUT / "method_c_bottom_up.csv")
    tornado.round(4).to_csv(OUT / "method_c_sensitivity.csv")
    recon.round(2).to_csv(OUT / "annual_energy_reconciled.csv")
    pk.round(4).to_csv(OUT / "peak_demand.csv")
    mon.round(4).to_csv(OUT / "monthly_shape_central.csv")
    proj.round(2).to_csv(OUT / "projections.csv")
    RESULTS_MD.write_text(write_results(cfg, a, b, bm, eg, c, tornado, recon, pk, mon, proj), encoding="utf-8", newline="\n")
    return {"a": a, "b": b, "b_matrix": bm, "egrid": eg, "c": c, "tornado": tornado, "recon": recon,
            "peak": pk, "monthly": mon, "proj": proj}


def main() -> None:
    r = run()
    recon, pk = r["recon"], r["peak"]
    print("Annual retail energy (TWh) and peak (MW):")
    for case in CASES:
        print(f"  {case:8s} {recon.loc[case,'retail_mwh']/1e6:5.2f} TWh  avg {recon.loc[case,'avg_mw_at_meter']:4.0f} MW  peak {pk.loc[case,'peak_mw']:4.0f} MW")
    print(f"  stress   {recon.loc['stress_low','retail_mwh']/1e6:.2f}-{recon.loc['stress_high','retail_mwh']/1e6:.2f} TWh")
    print(f"wrote {OUT.relative_to(ROOT)}/ and {RESULTS_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
