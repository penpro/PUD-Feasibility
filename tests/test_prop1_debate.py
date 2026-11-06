"""Claims about Prop 1's legal order, carbon prices and dam removal are re-read from the archived primary sources."""
import html
import re

import pytest
from conftest import ROOT

RAW = ROOT / "data" / "raw"


def _squash(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " "))


def _html(path) -> str:
    raw = path.read_bytes().decode("utf-8", errors="replace")
    raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    return _squash(html.unescape(re.sub(r"(?s)<[^>]+>", " ", raw)))


def _pdf(path, page: int | None = None) -> str:
    fitz = pytest.importorskip("fitz")
    doc = fitz.open(path)
    pages = [doc[page - 1]] if page else list(doc)
    return _squash(" ".join(p.get_text() for p in pages))


def _rcw(cite: str) -> str:
    return _pdf(RAW / "wa_rcw" / f"rcw_{cite}.pdf")


def test_a_district_may_study_electric_systems_and_needs_a_vote_only_to_build_or_buy():
    study = _rcw("54.16.010")
    assert "A district may make surveys, plans, investigations or studies" in study
    assert "generation, transmission or distribution" in study
    assert "vote" not in study.lower()
    vote = _rcw("54.08.070")
    assert "shall not construct or acquire any such electric facilities without the approval" in vote
    assert "At any general election held in an even-numbered year" in vote


def test_debt_vote_applies_to_general_debt_and_revenue_bonds_mention_no_vote():
    debt = _rcw("54.24.018")
    assert "three-fourths of one percent" in debt
    start = debt.index("(3) When the commission shall not desire to incur a general indebtedness")
    end = debt.find("(4)", start)
    subsection = debt[start:end if end > 0 else None]
    assert "revenue bonds" in subsection
    assert "vote" not in subsection.lower() and "elector" not in subsection.lower()


def test_utilities_are_eligible_for_no_cost_allowances():
    text = _rcw("70A.65.120")
    assert "consumer- owned electric utilities and investor-owned electric utilities" in text
    assert "mitigate the cost burden" in text
    assert "at no cost" in text


def test_kpud_says_the_order_was_its_own_choice_and_promises_no_second_vote():
    pub = RAW / "kpud_fact_publication" / "FINAL-KPUD-Prop-1-Fact-Publication.pdf"
    p2, p3 = _pdf(pub, 2), _pdf(pub, 3)
    assert "prudent to seek voter direction first" in p3
    assert "Approve financing or issuance of bonds" in p2
    assert "by the Board during a public meeting" in p2
    assert "the feasibility study would not move forward" in p2
    assert "second vote" not in _pdf(pub).lower()


def test_carbon_prices_are_settlement_prices_from_the_primary_reports():
    june = _pdf(RAW / "wa_ecology_auctions" / "ecology_pub_2614039.pdf")
    assert "sold at a settlement price of $64.56" in june
    sept = _html(RAW / "wa_ecology_auctions" / "ecology_news_2025-09-10_auction.html")
    assert "settlement price of $64.30" in sept
    assert "fixed at $60.43" in sept, "$60.43 is the reserve-auction price, not the September settlement"
    first = _html(RAW / "eia_today_in_energy" / "eia_tie_61544.html")
    assert "first allowance auction on February 28, 2023" in first
    assert "$48.50" in first


def test_sumas_figures_match_eia():
    assert "$1.87/MMBtu in 2024 through October" in _html(RAW / "eia_today_in_energy" / "eia_tie_63744.html")
    y2025 = _html(RAW / "eia_today_in_energy" / "eia_tie_66084.html")
    assert "$1.59 per million British thermal units (MMBtu) in 2025 through August" in y2025
    assert "$0.56/MMBtu in June" in y2025


def test_gas_plants_are_in_pses_own_supply_plan():
    raw = (RAW / "sec_puget_energy_10k_fy2025" / "psd-20251231.htm").read_bytes().decode("cp1252", errors="replace")
    text = _squash(html.unescape(re.sub(r"(?s)<[^>]+>", " ", raw)))
    assert "Gray's Harbor combined cycle contract for 665 MW" in text
    assert "to a combined cycle plant for 700 MW in 2028" in text
    assert "shortfall of 576 MW in 2026" in text
    assert "shortfall of 1,404 MW by 2030" in text


def test_dam_removal_needs_congress_and_the_cost_range_matches_crs():
    crs = _html(RAW / "crs_r48089" / "crs_R48089_2026-07-31.html")
    assert "generally have ranged from $10 billion to $31 billion" in crs
    assert "without action from Congress" in crs
    memo = _pdf(RAW / "presidential_memo_2025_columbia" / "DCPD-202500686.pdf")
    assert "Columbia River Basin" in memo and "June 12, 2025" in memo


def test_new_questions_and_objections_are_logged():
    text = (ROOT / "docs" / "open-questions.md").read_text(encoding="utf-8")
    for tag in ("OQ-16", "OQ-17", "OQ-18", "OQ-19", "OQ-20", "OQ-21", "OQ-22", "D-1", "D-2", "D-3", "D-4", "D-5"):
        assert f"| {tag} |" in text, tag


@pytest.mark.parametrize("rel", ["docs/index.html", "docs/findings.md", "docs/open-questions.md",
                                 "docs/help-wanted.yaml", "README.md"])
def test_public_docs_describe_prop_1_accurately(rel):
    """Prop 1 was a vote on authority that funded nothing; KPUD tied its study to it by choice."""
    text = (ROOT / rel).read_text(encoding="utf-8")
    bad = r"(?i)\b(block(s|ed|ing)?|kill(s|ed|ing)?)\s+(a|an|the|kpud'?s?)?\s*(\S+\s+){0,3}study\b|study prop(osition)? 1 would fund"
    assert not re.search(bad, text), f"{rel}: says Prop 1 or PSE blocked or funded a study"


def test_bpa_limits_match_the_policy_and_the_config():
    from model.common import load_config, val
    policy = _pdf(RAW / "bpa_provider_of_choice" / "provider-of-choice-policy-march-2024.pdf")
    assert "to a total of 200 aMW during the Provider of Choice contract period, with no more than 50 aMW added in any rate period" in policy
    assert "first come, first serve" in policy
    assert "only be able to purchase power at PF Tier 2 rates" in policy
    assert "September 30, 2044" in policy
    chwm = _pdf(RAW / "bpa_provider_of_choice" / "chwm-implementation-policy-20250814.pdf")
    assert "A new public is a newly formed public utility that is not an existing customer of Bonneville" in chwm
    assert "three years prior to service date" in chwm
    assert "two-year rate period" in chwm
    cfg = load_config()
    assert val(cfg, "context.bpa_new_public.tier1_total_amw") == 200
    assert val(cfg, "context.bpa_new_public.tier1_per_rate_period_amw") == 50


def test_f06_shares_match_the_model():
    import build_site
    k = build_site.build()["k"]
    findings = (ROOT / "docs" / "findings.md").read_text(encoding="utf-8")
    section = findings[findings.index("## F-06"):findings.index("## Corrections")]
    first = re.search(r"First rate period.*?\| (\d+%) \| \*\*(\d+%)\*\* \| (\d+%) \|", section).groups()
    cap = re.search(r"Full limit.*?\| (\d+%) \| \*\*(\d+%)\*\* \| (\d+%) \|", section).groups()
    assert first == (k["bpa_first_share_high"], k["bpa_first_share"], k["bpa_first_share_low"])
    assert cap == (k["bpa_cap_share_high"], k["bpa_cap_share"], k["bpa_cap_share_low"])
    oq = (ROOT / "docs" / "open-questions.md").read_text(encoding="utf-8")
    assert f"about {k['bpa_first_share']} at first and at most {k['bpa_cap_share']} later" in oq


def test_allowance_page_supports_the_eligibility_claim():
    page = _html(RAW / "wa_ecology_auctions" / "ecology_no_cost_allowances_page.html")
    assert "subject to the Clean Energy Transformation Act are eligible" in page
    assert "revised October 2026" in page
