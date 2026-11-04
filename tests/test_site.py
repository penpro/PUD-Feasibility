"""The website can't drift from the model, and every ask points somewhere real."""
import re

import pytest
from conftest import ROOT

import build_site


@pytest.fixture(scope="module")
def data():
    return build_site.build()


def test_site_data_is_current(data):
    on_disk = (ROOT / "docs" / "site-data.js").read_text(encoding="utf-8")
    assert on_disk == build_site.render_js(data), "docs/site-data.js is stale: run python scripts/build_site.py"


def test_help_wanted_md_is_current(data):
    on_disk = (ROOT / "docs" / "help-wanted.md").read_text(encoding="utf-8")
    assert on_disk == build_site.render_md(data), "docs/help-wanted.md is stale: run python scripts/build_site.py"


def test_every_bound_key_exists(data):
    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    keys = set(re.findall(r'data-k="([^"]+)"', html))
    assert keys, "index.html binds no numbers?"
    assert keys <= data["k"].keys(), f"unbuilt keys: {sorted(keys - data['k'].keys())}"


def test_asks_are_well_formed(data):
    templates = {p.name for p in (ROOT / ".github" / "ISSUE_TEMPLATE").glob("*.md")}
    groups = {g["id"] for g in data["groups"]}
    open_q = (ROOT / "docs" / "open-questions.md").read_text(encoding="utf-8")
    ids = [a["id"] for a in data["asks"]]
    assert len(ids) == len(set(ids)), "duplicate ask ids"
    for a in data["asks"]:
        assert a["template"] in templates, f"{a['id']}: no issue template {a['template']}"
        assert a["group"] in groups, f"{a['id']}: unknown group {a['group']}"
        assert a["priority"] in ("top", "high", "normal")
        for q in a["oq"]:
            assert f"| {q} |" in open_q, f"{a['id']}: {q} not in docs/open-questions.md"
        text = " ".join([a["title"], a["why"], *a["how"]])
        assert "{" not in text and "}" not in text, f"{a['id']}: unfilled placeholder"


def test_headline_numbers_match_model(data):
    from model.load import run
    r = run()
    assert data["k"]["central_twh"] == f"{r['recon'].loc['central', 'retail_mwh'] / 1e6:.2f}"
    assert data["k"]["peak_central"] == f"{r['peak'].loc['central', 'peak_mw']:,.0f}"
