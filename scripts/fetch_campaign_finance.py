"""Prop 1 campaign finance from the WA Public Disclosure Commission (PDC), via data.wa.gov.

    python scripts/fetch_campaign_finance.py            # query PDC, archive a snapshot if anything changed, rebuild CSVs
    python scripts/fetch_campaign_finance.py --offline  # rebuild the CSVs from archived snapshots only

Committees are found by the measure itself (jurisdiction "KITSAP PUD 01", 2026, stance for/against), not by name.
Each snapshot is saved unmodified under data/raw/wa_pdc_prop1/<date>/. The query strings are below and in
data/sources.yaml (S024). Individual donors are only ever pulled as counts and sums by category, never by name.
After a new snapshot, run `python scripts/sources.py build` to hash it.

Outputs (data/processed/campaign_finance/):
    prop1_committees.csv         one row per committee per snapshot: side, raised, spent, PDC link
    prop1_no_contributors.csv    the No committee's contributors (all organizations), latest snapshot
    prop1_by_category.csv        contribution counts and sums by side and contributor category, latest snapshot
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "wa_pdc_prop1"
OUT = ROOT / "data" / "processed" / "campaign_finance"
API = "https://data.wa.gov/resource/{}.json"
META = "https://data.wa.gov/api/views/{}.json"
COMMITTEES_DS, CONTRIB_DS = "3h9x-7bvm", "kv7h-kjye"
MEASURE = "jurisdiction='KITSAP PUD 01' AND election_year=2026 AND for_or_against in('for','against')"

QUERIES = {   # file name -> (dataset, SoQL params). Order matters only for readability.
    "committees.json": (COMMITTEES_DS, {
        "$select": "committee_id,filer_id,filer_name,for_or_against,ballot_number,jurisdiction,election_year,"
                   "election_date,reporting_option,contributions_amount,expenditures_amount,debts_amount,"
                   "updated_at,url",
        "$where": MEASURE, "$order": "for_or_against,filer_name"}),
    "contributions_no.json": (CONTRIB_DS, {
        "$select": "id,report_number,origin,filer_name,for_or_against,jurisdiction,election_year,amount,"
                   "cash_or_in_kind,receipt_date,description,contributor_category,contributor_name,url",
        "$where": MEASURE.replace("in('for','against')", "='against'"), "$order": "receipt_date,id",
        "$limit": "5000"}),
    "contributions_by_category.json": (CONTRIB_DS, {
        "$select": "for_or_against,contributor_category,cash_or_in_kind,count(*) as n,sum(amount) as total",
        "$where": MEASURE, "$group": "for_or_against,contributor_category,cash_or_in_kind",
        "$order": "for_or_against,contributor_category,cash_or_in_kind"}),
}
METADATA = {"metadata_committees.json": COMMITTEES_DS, "metadata_contributions.json": CONTRIB_DS}
UA = {"User-Agent": "kitsap-public-power-study (open-source research)"}


def query_url(dataset: str, params: dict) -> str:
    return API.format(dataset) + "?" + urllib.parse.urlencode(params)


def _get(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def snapshots() -> list[Path]:
    return sorted(p for p in RAW.glob("20*") if p.is_dir())


def fetch(today: str | None = None) -> Path | None:
    data = {name: _get(query_url(ds, params)) for name, (ds, params) in QUERIES.items()}
    prev = snapshots()
    if prev and all((prev[-1] / n).read_bytes() == b for n, b in data.items()):
        print(f"no change since {prev[-1].name}")
        return None
    dest = RAW / (today or date.today().isoformat())
    if dest.exists():
        sys.exit(f"{dest.relative_to(ROOT)} already exists with different data; archive by hand or rerun tomorrow")
    dest.mkdir(parents=True)
    for name, b in data.items():
        (dest / name).write_bytes(b)
    for name, ds in METADATA.items():
        (dest / name).write_bytes(_get(META.format(ds)))
    print(f"archived {dest.relative_to(ROOT)}\nnext: python scripts/sources.py build")
    return dest


def _load(snap: Path, name: str) -> list[dict]:
    return json.loads((snap / name).read_text(encoding="utf-8"))


def _money(x) -> float:
    return round(float(x or 0), 2)


def summarize(snap: Path) -> dict:
    """Everything the study quotes about Prop 1 money, computed from one archived snapshot."""
    comm = _load(snap, "committees.json")
    contrib = _load(snap, "contributions_no.json")
    by_cat = _load(snap, "contributions_by_category.json")
    side = {"against": [c for c in comm if c["for_or_against"] == "against"],
            "for": [c for c in comm if c["for_or_against"] == "for"]}
    no_raised = sum(_money(c.get("contributions_amount")) for c in side["against"])
    no_spent = sum(_money(c.get("expenditures_amount")) for c in side["against"])
    yes_raised = sum(_money(c.get("contributions_amount")) for c in side["for"])
    yes_spent = sum(_money(c.get("expenditures_amount")) for c in side["for"])
    donors = defaultdict(lambda: {"category": "", "Cash": 0.0, "In-kind": 0.0})
    for r in contrib:
        d = donors[r["contributor_name"]]
        d["category"] = r.get("contributor_category", "")
        d[r["cash_or_in_kind"]] = round(d[r["cash_or_in_kind"]] + _money(r["amount"]), 2)
    itemized_no = round(sum(_money(r["amount"]) for r in contrib), 2)
    pse = sum(v["Cash"] + v["In-kind"] for k, v in donors.items() if k.strip().lower() == "puget sound energy")
    return {
        "snapshot": snap.name, "committees": comm, "donors": dict(donors), "by_category": by_cat,
        "no_raised": round(no_raised, 2), "no_spent": round(no_spent, 2), "itemized_no": itemized_no,
        "yes_raised": round(yes_raised, 2), "yes_spent": round(yes_spent, 2),
        "pse": round(pse, 2), "pse_share": pse / no_raised if no_raised else 0.0,
        "no_names": [c["filer_name"] for c in side["against"]], "yes_names": [c["filer_name"] for c in side["for"]],
    }


def rebuild() -> dict:
    snaps = snapshots()
    if not snaps:
        sys.exit("no snapshots in data/raw/wa_pdc_prop1/: run without --offline first")
    OUT.mkdir(parents=True, exist_ok=True)
    side_name = {"against": "No", "for": "Yes"}
    with (OUT / "prop1_committees.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["snapshot", "side", "committee", "raised", "spent", "reporting", "pdc_updated_at", "pdc_url"])
        for snap in snaps:
            for c in _load(snap, "committees.json"):
                w.writerow([snap.name, side_name[c["for_or_against"]], c["filer_name"],
                            f"{_money(c.get('contributions_amount')):.2f}", f"{_money(c.get('expenditures_amount')):.2f}",
                            c.get("reporting_option", ""), c.get("updated_at", "")[:10], c.get("url", {}).get("url", "")])
    s = summarize(snaps[-1])
    with (OUT / "prop1_no_contributors.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["snapshot", "contributor", "category", "cash", "in_kind", "total", "share_of_no_raised"])
        for name, d in sorted(s["donors"].items(), key=lambda kv: -(kv[1]["Cash"] + kv[1]["In-kind"])):
            tot = d["Cash"] + d["In-kind"]
            w.writerow([s["snapshot"], name, d["category"], f"{d['Cash']:.2f}", f"{d['In-kind']:.2f}", f"{tot:.2f}",
                        f"{tot / s['no_raised']:.4f}"])
    with (OUT / "prop1_by_category.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["snapshot", "side", "contributor_category", "cash_or_in_kind", "n", "total"])
        for r in s["by_category"]:
            w.writerow([s["snapshot"], side_name[r["for_or_against"]], r.get("contributor_category", ""),
                        r.get("cash_or_in_kind", ""), r["n"], f"{_money(r['total']):.2f}"])
    if abs(s["itemized_no"] - s["no_raised"]) > 0.01:
        print(f"WARNING: No-side itemized contributions ${s['itemized_no']:,.2f} != committee total "
              f"${s['no_raised']:,.2f} (reports may be mid-update)")
    return s


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="do not query PDC; rebuild from archived snapshots")
    args = ap.parse_args(argv)
    if not args.offline:
        fetch()
    s = rebuild()
    print(f"snapshot {s['snapshot']}: No raised ${s['no_raised']:,.2f}, spent ${s['no_spent']:,.2f} "
          f"({'; '.join(s['no_names'])})")
    print(f"  PSE ${s['pse']:,.2f} = {s['pse_share']:.1%} of No raised")
    print(f"  Yes raised ${s['yes_raised']:,.2f}, spent ${s['yes_spent']:,.2f} ({'; '.join(s['yes_names'])})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
