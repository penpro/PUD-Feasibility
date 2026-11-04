"""Prop 1 campaign finance: re-derived from the archived PDC filings, and quoted correctly everywhere."""
import csv

import pytest
from conftest import ROOT

import fetch_campaign_finance as pdc


@pytest.fixture(scope="module")
def first():
    """The 2026-11-04 snapshot: the figures the docs were written from."""
    return pdc.summarize(pdc.RAW / "2026-11-04")


@pytest.fixture(scope="module")
def latest():
    return pdc.summarize(pdc.snapshots()[-1])


def test_snapshot_values(first):
    assert first["pse"] == 2_318_178.33
    assert first["no_raised"] == 2_401_233.33
    assert first["no_spent"] == 2_304_528.34
    assert first["yes_raised"] == 9_055.00
    assert first["yes_spent"] == 7_252.97
    assert round(first["pse_share"], 3) == 0.965


def test_committees_found_by_measure_not_name(first):
    assert len(first["no_names"]) == 1 and "Puget Sound Energy" in first["no_names"][0]
    assert first["yes_names"] == ["Unplug PSE"]


def test_itemized_contributions_reconcile(latest):
    """The No side's itemized contributions sum to the committee's reported total."""
    assert latest["itemized_no"] == pytest.approx(latest["no_raised"], abs=0.01)


def test_no_individual_donor_names_archived():
    for snap in pdc.snapshots():
        rows = pdc._load(snap, "contributions_no.json")
        assert all(r["contributor_category"] != "Individual" for r in rows), \
            "individual donors must only appear as counts/sums (contributions_by_category.json)"
        for r in pdc._load(snap, "contributions_by_category.json"):
            assert "contributor_name" not in r


def test_processed_csvs_are_current(latest):
    with (pdc.OUT / "prop1_committees.csv").open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["snapshot"] == latest["snapshot"]]
    by_side = {r["side"]: r for r in rows}
    assert float(by_side["No"]["raised"]) == latest["no_raised"]
    assert float(by_side["Yes"]["raised"]) == latest["yes_raised"]


def test_docs_quote_the_filings(first):
    pse, no, yes = f"${first['pse']:,.0f}", f"${first['no_raised']:,.0f}", f"${first['yes_raised']:,.0f}"
    findings = (ROOT / "docs" / "findings.md").read_text(encoding="utf-8")
    oq = (ROOT / "docs" / "open-questions.md").read_text(encoding="utf-8")
    for text, where in ((findings, "findings.md"), (oq, "open-questions.md")):
        for figure in (pse, no, yes, f"{first['pse_share']:.1%}"):
            assert figure in text, f"{where} should quote {figure} (S024)"
