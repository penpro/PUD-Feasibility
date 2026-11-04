"""Track the KPUD Proposition 1 count until certification (Kitsap County canvass: Nov 24, 2026).

    python scripts/fetch_election_results.py            # fetch the live report, archive it, update the CSV
    python scripts/fetch_election_results.py --offline  # rebuild the CSV from archived snapshots only

Each new count is saved unmodified as data/raw/election_2026/results_<run date>_<run time>.html
(named by the report's own run timestamp) and parsed into data/processed/election/prop1_counts.csv.
After a new snapshot is archived, run `python scripts/sources.py build` to hash it.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import urllib.request
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP_DIR = ROOT / "data" / "raw" / "election_2026"
CSV_PATH = ROOT / "data" / "processed" / "election" / "prop1_counts.csv"
URL = "https://www.kitsap.gov/auditor/Documents/results.html"
CONTEST = "Kitsap County Public Utility District No. 1"   # exact header; commissioner races have longer titles
FIELDS = ["run_datetime", "official", "registered_voters", "ballots_tabulated", "turnout",
          "yes", "no", "yes_pct", "no_pct", "undervotes", "overvotes", "snapshot"]


class _Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.chunks: list[str] = []
        self.meta: dict[str, str] = {}
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        if tag == "meta":
            a = dict(attrs)
            if "name" in a and "content" in a:
                self.meta[a["name"]] = a["content"]

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1

    def handle_data(self, data):
        t = data.replace("\xa0", " ").strip()
        if t and not self._skip:
            self.chunks.append(t)


def _int(s: str) -> int:
    return int(s.replace(",", ""))


def parse(html: str) -> dict:
    p = _Text()
    p.feed(html)
    c = p.chunks
    i = c.index("Run Time")
    run_time = c[i + 1]
    j = c.index("Run Date")
    run_date = c[j + 1]
    run_dt = datetime.strptime(f"{run_date} {run_time}", "%m/%d/%Y %I:%M %p")
    k = c.index(CONTEST)
    block = c[k:k + 40]

    def after(label: str, n: int = 1) -> str:
        idx = block.index(label)
        return block[idx + n]

    yes, yes_pct = _int(after("Yes")), after("Yes", 2)
    no, no_pct = _int(after("No")), after("No", 2)
    reg = _int(p.meta["TotalRegisteredVoters"])
    tab = _int(p.meta["TotalTabulatedBallots"])
    return {
        "run_datetime": run_dt.isoformat(timespec="minutes"),
        "official": p.meta.get("LabelReportsAsOfficial", "").lower() == "true",
        "registered_voters": reg,
        "ballots_tabulated": tab,
        "turnout": round(tab / reg, 4),
        "yes": yes, "no": no, "yes_pct": yes_pct, "no_pct": no_pct,
        "undervotes": _int(after("Undervotes:")), "overvotes": _int(after("Overvotes:")),
    }


def snapshot_name(rec: dict) -> str:
    dt = datetime.fromisoformat(rec["run_datetime"])
    return f"results_{dt:%Y-%m-%d_%H%M}.html"


def rebuild_csv() -> list[dict]:
    rows = []
    for f in sorted(SNAP_DIR.glob("results_*.html")):
        rec = parse(f.read_bytes().decode("utf-8", errors="replace"))
        rec["snapshot"] = f.relative_to(ROOT).as_posix()
        rows.append(rec)
    rows.sort(key=lambda r: r["run_datetime"])
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return rows


def fetch() -> Path | None:
    req = urllib.request.Request(URL, headers={"User-Agent": "kitsap-public-power-study (open-source research)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    rec = parse(raw.decode("utf-8", errors="replace"))
    dest = SNAP_DIR / snapshot_name(rec)
    if dest.exists():
        print(f"no new count: latest report is still {rec['run_datetime']} ({dest.name})")
        return None
    dest.write_bytes(raw)
    print(f"archived new count {rec['run_datetime']} -> {dest.relative_to(ROOT)}")
    print("next: python scripts/sources.py build")
    return dest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="do not fetch; rebuild CSV from archived snapshots")
    args = ap.parse_args(argv)
    if not args.offline:
        fetch()
    rows = rebuild_csv()
    for r in rows:
        status = "OFFICIAL" if r["official"] else "unofficial"
        print(f"{r['run_datetime']}  {status:10s}  Yes {r['yes']:>7,} ({r['yes_pct']:>7})  No {r['no']:>7,} ({r['no_pct']:>7})"
              f"  tabulated {r['ballots_tabulated']:,}/{r['registered_voters']:,} ({r['turnout']:.1%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
