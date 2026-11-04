"""Build the voter-facing website's data from the model, so the site's numbers can't go stale.

    python scripts/build_site.py

Writes
  docs/site-data.js     window.SITE_DATA = {...}  (every number on docs/index.html comes from here)
  docs/help-wanted.md   GitHub-readable version of docs/help-wanted.yaml

docs/index.html is hand-written layout and prose. Any element with data-k="key" is filled from
SITE_DATA.k[key]. tests/test_site.py fails if index.html uses a key that isn't built here, or if
site-data.js is out of date.
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from model import eia861  # noqa: E402
from model.common import load_config, val  # noqa: E402
from model.load import run  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
import fetch_campaign_finance as pdc  # noqa: E402

DOCS = ROOT / "docs"
REPO = "https://github.com/penpro/PUD-Feasibility"
SITE_JS = DOCS / "site-data.js"
ASKS_YAML = DOCS / "help-wanted.yaml"
ASKS_MD = DOCS / "help-wanted.md"
ELECTION_CSV = ROOT / "data" / "processed" / "election" / "prop1_counts.csv"
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def comma(x: float) -> str:
    return f"{x:,.0f}"


def nice_date(d: datetime, with_time: bool = False) -> str:
    s = f"{d:%b} {d.day}, {d.year}"
    if with_time:
        h = d.hour % 12 or 12
        s += f", {h}:{d:%M} {'AM' if d.hour < 12 else 'PM'}"
    return s


def build() -> dict:
    cfg = load_config()
    r = run()
    recon, pk, mon, proj, tor, a = r["recon"], r["peak"], r["monthly"], r["proj"], r["tornado"], r["a"]
    bench = eia861.benchmarks()

    with ELECTION_CSV.open(encoding="utf-8") as fh:
        election = list(csv.DictReader(fh))[-1]
    run_dt = datetime.fromisoformat(election["run_datetime"])
    money = pdc.summarize(pdc.snapshots()[-1])   # Prop 1 campaign finance (S024)

    res = "load.bottom_up.residential_mwh_per_customer"
    home_kwh = {c: val(cfg, res, c) * 1000 / 12 for c in ("low", "central", "high")}
    central = recon.loc["central", "retail_mwh"]
    winter = mon["ratio_to_annual_avg"]
    y_last = cfg["settings"]["projection_years"][-1]
    by = cfg["settings"]["base_year"]

    k = {
        # energy
        "central_twh": f"{central / 1e6:.2f}",
        "central_bkwh": f"{central / 1e6:.1f}",
        "low_twh": f"{recon.loc['low', 'retail_mwh'] / 1e6:.2f}",
        "high_twh": f"{recon.loc['high', 'retail_mwh'] / 1e6:.2f}",
        "low_bkwh": f"{recon.loc['low', 'retail_mwh'] / 1e6:.1f}",
        "high_bkwh": f"{recon.loc['high', 'retail_mwh'] / 1e6:.1f}",
        "stress_low_twh": f"{recon.loc['stress_low', 'retail_mwh'] / 1e6:.2f}",
        "stress_high_twh": f"{recon.loc['stress_high', 'retail_mwh'] / 1e6:.2f}",
        "avg_mw": comma(recon.loc["central", "avg_mw_at_meter"]),
        "avg_mw_losses": comma(pk.loc["central", "avg_mw_system"]),
        "peak_central": comma(pk.loc["central", "peak_mw"]),
        "peak_low": comma(pk.loc["low", "peak_mw"]),
        "peak_high": comma(pk.loc["high", "peak_mw"]),
        "peak_ratio": f"{pk.loc['central', 'peak_mw'] / pk.loc['central', 'avg_mw_system']:.1f}",
        "base_year": str(by),
        # the claims we tested
        "findenergy_twh": f"{a['total_mwh'] / 1e6:.2f}",
        "findenergy_bkwh": f"{a['total_mwh'] / 1e6:.1f}",
        "findenergy_pct_over": f"{a['total_mwh'] / central - 1:.0%}",
        "state_pc_mwh": f"{a['state_per_capita_mwh']}",
        "kuow_mw": comma(val(cfg, "load.kuow_claim_mw")),
        # households
        "customers": comma(val(cfg, "load.bottom_up.pse_kitsap_customers", "central")),
        "home_kwh_month": comma(round(home_kwh["central"], -1)),
        "home_kwh_month_low": comma(round(home_kwh["low"], -1)),
        "home_kwh_month_high": comma(round(home_kwh["high"], -1)),
        "pse_home_kwh_month": comma(round(bench.loc[eia861.PSE, "res_mwh_per_customer"] * 1000 / 12, -1)),
        "com_swing_pct": f"{tor.loc['commercial_mwh_per_customer', 'swing_pct_of_central']:.0%}",
        # seasons and growth
        "winter_peak_month": MONTHS[int(winter.idxmax()) - 1],
        "winter_pct": f"{winter.max() - 1:.0%}",
        "low_month": MONTHS[int(winter.idxmin()) - 1],
        "low_month_pct": f"{1 - winter.min():.0%}",
        "ev_count": comma(val(cfg, "load.growth.ev_stock_2026")),
        "proj_year": str(y_last),
        "proj_central_twh": f"{proj.loc[('central', y_last), 'retail_mwh'] / 1e6:.2f}",
        "proj_low_twh": f"{proj.loc[('low', y_last), 'retail_mwh'] / 1e6:.1f}",
        "proj_high_twh": f"{proj.loc[('high', y_last), 'retail_mwh'] / 1e6:.1f}",
        "proj_growth_pct": f"{proj.loc[('central', y_last), 'retail_mwh'] / central - 1:.0%}",
        "proj_evs": comma(val(cfg, "load.growth.ev_stock_2045", "central")),
        # election
        "yes_pct": election["yes_pct"],
        "no_pct": election["no_pct"],
        "yes_votes": comma(int(election["yes"])),
        "no_votes": comma(int(election["no"])),
        "turnout_pct": f"{float(election['turnout']):.1%}",
        "count_time": nice_date(run_dt, with_time=True),
        "count_status": "Official (certified)" if election["official"] == "True" else "Unofficial",
        # campaign finance (PDC, S024)
        "pdc_pse": f"${comma(money['pse'])}",
        "pdc_pse_share": f"{money['pse_share']:.1%}",
        "pdc_no_raised": f"${comma(money['no_raised'])}",
        "pdc_no_spent": f"${comma(money['no_spent'])}",
        "pdc_yes_raised": f"${comma(money['yes_raised'])}",
        "pdc_yes_spent": f"${comma(money['yes_spent'])}",
        "pdc_as_of": nice_date(datetime.fromisoformat(money['snapshot'])),
        # rate context (EIA average revenue per kWh, residential)
        **{f"cents_{key}": f"{bench.loc[uid, 'res_cents_per_kwh']:.1f}" for key, uid in
           (("pse", 15500), ("jefferson", 59013), ("mason3", 15419), ("clallam", 3644),
            ("snohomish", 17470), ("penlight", 14668))},
        # meta
        "as_of": nice_date(datetime.fromisoformat(str(cfg["meta"]["config_as_of"]))),
        "study_version": cfg["meta"]["study_version"],
    }

    charts = {
        "energy": [
            {"label": "Number you may have seen (FindEnergy)", "value": a["total_mwh"] / 1e6, "kind": "claim"},
            {"label": "This study's estimate", "value": central / 1e6,
             "low": recon.loc["low", "retail_mwh"] / 1e6, "high": recon.loc["high", "retail_mwh"] / 1e6, "kind": "estimate"},
        ],
        "monthly": [{"month": MONTHS[m - 1], "avg_mw": float(row.avg_mw_at_meter), "ratio": float(row.ratio_to_annual_avg),
                     "mwh": float(row.total_mwh)} for m, row in mon.iterrows()],
        "monthly_avg_mw": central / 8760,
        "projection": [{"year": int(y), "low": proj.loc[("low", y), "retail_mwh"] / 1e6,
                        "central": proj.loc[("central", y), "retail_mwh"] / 1e6,
                        "high": proj.loc[("high", y), "retail_mwh"] / 1e6}
                       for y in cfg["settings"]["projection_years"]],
        "election": {"yes": int(election["yes"]), "no": int(election["no"])},
    }

    spec = yaml.safe_load(ASKS_YAML.read_text(encoding="utf-8"))
    asks = []
    for ask in spec["asks"]:
        fill = lambda s: s.format_map(k)  # noqa: E731
        url = f"{REPO}/issues/new?template={quote(ask['template'])}&title={quote(ask['issue_title'])}"
        asks.append({**ask, "why": fill(ask["why"]), "how": [fill(h) for h in ask["how"]],
                     "title": fill(ask["title"]), "issue_url": url, "links": ask.get("links", [])})
    return {"k": k, "charts": charts, "groups": spec["groups"], "asks": asks, "repo": REPO}


def render_js(data: dict) -> str:
    body = json.dumps(data, indent=1, ensure_ascii=False, default=float)
    return ("// GENERATED by scripts/build_site.py from the model and docs/help-wanted.yaml. Do not edit.\n"
            f"window.SITE_DATA = {body};\n")


def render_md(data: dict) -> str:
    out = ["# Help wanted", "",
           "<!-- GENERATED by scripts/build_site.py from docs/help-wanted.yaml. Do not edit by hand. -->", "",
           "Specific things this study needs, by who can help. The same list, with buttons, is on the "
           "[project website](https://penpro.github.io/PUD-Feasibility/#help). Each item opens a pre-filled GitHub "
           "issue (free account needed). Before starting something big, open an **I'll take this on** issue so two "
           "people don't do the same work.", ""]
    badge = {"top": "🔴 most needed", "high": "🟠 high", "normal": ""}
    for g in data["groups"]:
        out += [f"## {g['title']}", "", g["blurb"], ""]
        for a in (x for x in data["asks"] if x["group"] == g["id"]):
            tag = f" · {badge[a['priority']]}" if badge[a["priority"]] else ""
            oq = f" · {', '.join(a['oq'])}" if a["oq"] else ""
            out += [f"### {a['id']}. {a['title']}", "", f"*{a['effort']}{tag}{oq}*", "", a["why"], ""]
            out += [f"{i}. {step}" for i, step in enumerate(a["how"], 1)]
            out += [""]
            for link in a["links"]:
                out.append(f"- [{link['text']}]({link['url']})")
            out += [f"- **[Start: open a pre-filled issue]({a['issue_url']})**", ""]
    return "\n".join(out)


def main() -> int:
    data = build()
    SITE_JS.write_text(render_js(data), encoding="utf-8", newline="\n")
    ASKS_MD.write_text(render_md(data), encoding="utf-8", newline="\n")
    print(f"wrote {SITE_JS.relative_to(ROOT)} ({len(data['k'])} values, {len(data['asks'])} asks) and {ASKS_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
