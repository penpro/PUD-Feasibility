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


def test_ask_count_in_docs_matches_the_list(data):
    n = len(data["asks"])
    for rel in ("README.md", "CONTRIBUTING.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        counts = re.findall(r"(\d+) specific (?:asks|things)", text)
        assert counts and all(int(c) == n for c in counts), f"{rel} says {counts}, but help-wanted.yaml has {n} asks"


GAP_STATUSES = {"Open", "Partly answered", "Requests sent", "Waiting on regulator"}


def _open_questions() -> dict[str, tuple[str, str]]:
    """OQ id -> (priority, status), from the table in docs/open-questions.md."""
    text = (ROOT / "docs" / "open-questions.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| (OQ-\d+) \| (P\d) \|.*\| ([^|]*) \|\s*$", text, flags=re.M)
    return {oq: (pri, status.strip()) for oq, pri, status in rows}


def test_every_gap_has_a_real_plan(data):
    questions = _open_questions()
    ask_ids = {a["id"] for a in data["asks"]}
    groups = {g["id"] for g in data["gap_groups"]}
    assert data["gaps"], "no gaps listed"
    for gap in data["gaps"]:
        name = gap["oq"][0]
        assert gap["group"] in groups, name
        assert gap["status"] in GAP_STATUSES, name
        assert len(gap["plan"]) >= 1 and gap["who"] and gap["closed_when"] and gap["known"] and gap["unknown"], name
        assert all(q in questions for q in gap["oq"]), f"{name}: unknown open question"
        assert set(gap["asks"]) <= ask_ids, f"{name}: unknown ask"
        text = " ".join([gap["question"], gap["known"], gap["unknown"], gap["who"], gap["closed_when"], *gap["plan"]])
        assert "{" not in text and "}" not in text, f"{name}: unfilled placeholder"


def test_biggest_unknowns_are_all_listed(data):
    listed = {q for gap in data["gaps"] for q in gap["oq"]}
    questions = _open_questions()
    open_p1 = {q for q, (pri, status) in questions.items() if pri == "P1" and not status.startswith("Answered")}
    assert open_p1 and open_p1 <= listed, f"open P1 questions missing from docs/gaps.yaml: {sorted(open_p1 - listed)}"
    from_the_prop1_review = {"OQ-06", "OQ-11", "OQ-16", "OQ-17", "OQ-18", "OQ-19", "OQ-20", "OQ-21", "OQ-22"}
    assert from_the_prop1_review <= listed, sorted(from_the_prop1_review - listed)


def test_open_questions_block_is_current(data):
    on_disk = (ROOT / "docs" / "open-questions.md").read_text(encoding="utf-8")
    assert on_disk == build_site.splice_gaps(on_disk, build_site.render_gaps_md(data)), \
        "docs/open-questions.md is stale: run python scripts/build_site.py"
