"""Readers for EIA Form 861 (annual) and 861M (monthly) workbooks, plus the benchmark table.

EIA workbooks have a three-row header. We flatten it to
  * utility-characteristic columns -> their own name ("Utility Number", "State", ...)
  * data columns                   -> "CLASS|Metric", e.g. "RESIDENTIAL|Sales" (MWh)
EIA writes missing values as "."; they become NaN.

    python -m model.eia861     # writes data/processed/eia861_2025_benchmarks.csv
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import HOURS_PER_YEAR, PROCESSED, RAW

ANNUAL_DIR = RAW / "eia861_2025"
MONTHLY_DIR = RAW / "eia861m"
ANNUAL_YEAR = 2025
PSE = 15500

# Benchmarks: PSE itself plus the nearest public utilities (similar climate and housing stock).
BENCHMARKS = {
    15500: "Puget Sound Energy (system-wide)",
    59013: "PUD No 1 of Jefferson County",
    15419: "PUD No 3 of Mason County",
    3644: "PUD No 1 of Clallam County",
    14668: "Peninsula Light Company",
    17470: "PUD No 1 of Snohomish County",
}


def _flatten(header: pd.DataFrame, mode: str) -> list[str]:
    top = header.iloc[0].ffill()
    mid = header.iloc[1].ffill()
    leaf = header.iloc[2]
    names = []
    for a, b, c in zip(top, mid, leaf):
        a_up = str(a).strip().upper()
        if mode == "leaf" or a_up.startswith("UTILITY CHAR"):
            names.append(str(c).split("\n")[0].strip())
        else:
            names.append(f"{a_up}|{str(b).strip()}")
    return names


def _read(path: Path, sheet: str, mode: str) -> pd.DataFrame:
    header = pd.read_excel(path, sheet_name=sheet, header=None, nrows=3)
    df = pd.read_excel(path, sheet_name=sheet, header=None, skiprows=3)
    df.columns = _flatten(header, mode)
    for c in df.columns:
        if "|" in c or c in NUMERIC_LEAF:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["Utility Number"] = pd.to_numeric(df["Utility Number"], errors="coerce")
    return df


NUMERIC_LEAF = {
    "Summer Peak Demand", "Winter Peak Demand", "Sales to Ultimate Customers",
    "Total Energy Losses", "Total Sources", "Sales for Resale", "Net Generation",
    "Wholesale Power Purchases", "Year", "Month", "Data Year",
}


def annual_sales(path: Path = ANNUAL_DIR / f"Sales_Ult_Cust_{ANNUAL_YEAR}.xlsx") -> pd.DataFrame:
    return _read(path, "States", "class_metric")


def operational(path: Path = ANNUAL_DIR / f"Operational_Data_{ANNUAL_YEAR}.xlsx") -> pd.DataFrame:
    return _read(path, "States", "leaf")


def service_territory(county: str, state: str = "WA",
                      path: Path = ANNUAL_DIR / f"Service_Territory_{ANNUAL_YEAR}.xlsx") -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Counties_States")
    return df[(df["State"] == state) & (df["County"].str.lower() == county.lower())]


def monthly_sales(year: int, utility: int = PSE) -> pd.DataFrame:
    df = _read(MONTHLY_DIR / f"sales_ult_cust_{year}.xlsx", 0, "class_metric")
    df = df[df["Utility Number"] == utility].copy()
    # Bundled service only if the file distinguishes service types.
    for col in ("Service Type", "Part"):
        if col in df.columns and df[col].nunique() > 1:
            keep = "Bundled" if col == "Service Type" else "A"
            df = df[df[col] == keep]
    df["Year"] = df["Year"].astype(int)
    df["Month"] = df["Month"].astype(int)
    return df.sort_values("Month")


def benchmarks() -> pd.DataFrame:
    """Per-customer use, class mix, losses and load factor for the benchmark utilities (EIA 2025)."""
    s = annual_sales()
    o = operational()
    rows = []
    for uid, name in BENCHMARKS.items():
        bundled = s[(s["Utility Number"] == uid) & (s["Part"] == "A")]
        delivery = s[(s["Utility Number"] == uid) & (s["Part"] == "C")]
        if len(bundled) != 1:
            raise ValueError(f"expected one bundled row for utility {uid}, got {len(bundled)}")
        b = bundled.iloc[0]
        delivery_mwh = float(delivery["TOTAL|Sales"].fillna(0).sum())
        op = o[o["Utility Number"] == uid].iloc[0]
        losses = float(op["Total Energy Losses"])
        peak = float(max(op["Winter Peak Demand"], op["Summer Peak Demand"]))
        retail = float(b["TOTAL|Sales"])
        system_energy = retail + delivery_mwh + losses   # energy into the system to serve own retail load
        rows.append({
            "utility_number": uid,
            "utility": name,
            "year": ANNUAL_YEAR,
            "res_customers": b["RESIDENTIAL|Customers"],
            "res_mwh": b["RESIDENTIAL|Sales"],
            "com_customers": b["COMMERCIAL|Customers"],
            "com_mwh": b["COMMERCIAL|Sales"],
            "ind_customers": b["INDUSTRIAL|Customers"],
            "ind_mwh": b["INDUSTRIAL|Sales"],
            "total_customers": b["TOTAL|Customers"],
            "bundled_retail_mwh": retail,
            "delivery_only_mwh": delivery_mwh,
            "losses_mwh": losses,
            "winter_peak_mw": op["Winter Peak Demand"],
            "summer_peak_mw": op["Summer Peak Demand"],
            "res_mwh_per_customer": b["RESIDENTIAL|Sales"] / b["RESIDENTIAL|Customers"],
            "com_mwh_per_customer": b["COMMERCIAL|Sales"] / b["COMMERCIAL|Customers"],
            "res_customer_share": b["RESIDENTIAL|Customers"] / b["TOTAL|Customers"],
            "res_energy_share": b["RESIDENTIAL|Sales"] / retail,
            "loss_fraction": losses / system_energy,
            "load_factor": system_energy / HOURS_PER_YEAR / peak,
            "res_avg_bill_usd_per_month": b["RESIDENTIAL|Revenues"] * 1000 / b["RESIDENTIAL|Customers"] / 12,
            "res_cents_per_kwh": b["RESIDENTIAL|Revenues"] * 1000 / (b["RESIDENTIAL|Sales"] * 1000) * 100,
        })
    return pd.DataFrame(rows).set_index("utility_number")


def main() -> None:
    out = PROCESSED / "eia861_2025_benchmarks.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df = benchmarks()
    df.round(4).to_csv(out)
    print(df[["utility", "res_mwh_per_customer", "com_mwh_per_customer", "res_customer_share",
              "loss_fraction", "load_factor", "res_cents_per_kwh"]].round(4).to_string())
    print("\nUtilities EIA lists in Kitsap County:")
    print(service_territory("Kitsap")[["Utility Number", "Utility Name"]].to_string(index=False))
    print(f"\nwrote {out.relative_to(PROCESSED.parents[1])}")


if __name__ == "__main__":
    main()
