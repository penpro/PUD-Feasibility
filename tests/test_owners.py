"""PSE owners' figures in model/config.yaml are re-derived from the archived Puget Energy 10-K (S025)."""
import html
import re

import pytest
from conftest import ROOT

from model.common import load_config, val

TENK = ROOT / "data" / "raw" / "sec_puget_energy_10k_fy2025" / "psd-20251231.htm"
OWNERS = ("British Columbia Investment Management", "Alberta Investment Management", "Ontario Municipal Employee",
          "PGGM Vermogensbeheer", "Macquarie Washington Clean Energy Investment", "Ontario Teachers")


@pytest.fixture(scope="module")
def text():
    raw = TENK.read_bytes().decode("cp1252", errors="replace")
    raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    flat = html.unescape(re.sub(r"(?s)<[^>]+>", " ", raw)).replace("\xa0", " ")
    flat = re.sub(r"\s+", " ", flat)
    return flat[flat.find("UNITED STATES SECURITIES AND EXCHANGE COMMISSION"):]   # skip the hidden XBRL header


def _nums(s: str) -> list[int]:
    """'( 62,887 ) ( 175,861 )' -> [62887, 175861]; a dash or blank cell -> 0."""
    out = []
    for tok in re.findall(r"\(?\s*[\d,]+\s*\)?|[^\s\d(),$]+", s):
        digits = re.sub(r"\D", "", tok)
        out.append(int(digits) if digits else 0)
    return out


def _statement(text: str, heading: str) -> str:
    i = text.find(heading)
    assert i >= 0, f"heading not found: {heading}"
    return text[i:i + 20000]


def test_owners_named(text):
    for name in OWNERS:
        assert name in text, name


def test_net_income_matches_10k(text):
    stmt = _statement(text, "PUGET ENERGY, INC. CONSOLIDATED STATEMENTS OF CASH FLOWS")
    m = re.search(r"Net Income \(Loss\) \$ ([\d,]+) \$ ([\d,]+) \$ ([\d,]+)", stmt)
    assert m, "net income row not found"
    cfg = load_config()
    for year, got in zip((2025, 2024, 2023), m.groups()):
        assert val(cfg, f"context.pse_owners.net_income_{year}") == int(got.replace(",", "")) * 1000


def test_dividends_and_contributions_match_10k(text):
    stmt = _statement(text, "PUGET ENERGY, INC. CONSOLIDATED STATEMENTS OF CASH FLOWS")
    m = re.search(r"Dividends paid (.{0,60}?) Capital contribution (.{0,40}?) Proceeds", stmt)
    assert m, "financing rows not found"
    div, cap = _nums(m.group(1))[:3], _nums(m.group(2))[:3]
    cfg = load_config()
    for year, d, c in zip((2025, 2024, 2023), div, cap):
        assert val(cfg, f"context.pse_owners.dividends_paid_{year}") == d * 1000
        assert val(cfg, f"context.pse_owners.capital_contribution_{year}") == c * 1000


def test_counter_rate_is_2025_net_income_per_second():
    import build_site
    d = build_site.build()
    c = d["owners_counter"]
    assert c["start"] == "2026-11-03T00:00:00-08:00"
    assert c["per_second"] == pytest.approx(369_368_000 / (365 * 86400))
    assert d["k"]["owners_per_day"] == "$1.01 million"
