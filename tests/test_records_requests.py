"""Records-request letters: one source, no drift, no personal details on GitHub."""
import re

import pytest
from conftest import ROOT

import build_records_requests as brr

DUMMY = {"name": "Test Person", "email": "test@example.org", "phone": "", "address": ["1 A St", "Town, WA 98000"],
         "affiliation": "Kitsap Public Power Feasibility Study (independent, open source)",
         "affiliation_url": "https://github.com/penpro/PUD-Feasibility"}

REQUESTS = [brr.load_request(p) for p in brr.request_files()]


def test_there_is_at_least_one_request():
    assert REQUESTS


@pytest.mark.parametrize("req", REQUESTS, ids=lambda r: r["id"])
def test_md_block_is_current(req):
    md = brr.md_path(req).read_text(encoding="utf-8")
    assert brr.splice_md(md, brr.render_md_block(req), "md") == md, \
        "records-request .md is stale: run python scripts/build_records_requests.py --md-only"


@pytest.mark.parametrize("req", REQUESTS, ids=lambda r: r["id"])
def test_agencies_are_complete(req):
    ids = [a["id"] for a in req["agencies"]]
    assert len(ids) == len(set(ids))
    for a in req["agencies"]:
        assert re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]+", a["email"]), a["id"]
        assert a["portal"].startswith("https://"), a["id"]
        assert len(a["address"]) >= 3 and re.search(r"WA \d{5}", a["address"][-1]), a["id"]
        assert a["checked"] and a["scope"], a["id"]


@pytest.mark.parametrize("req", REQUESTS, ids=lambda r: r["id"])
def test_letter_and_email_carry_every_item(req):
    for a in req["agencies"]:
        tex = brr.render_tex(req, a, DUMMY)
        mail = brr.render_email(req, a, DUMMY, "x.pdf")
        assert tex.count(r"\item ") == len(req["items"])
        for i in range(1, len(req["items"]) + 1):
            assert f"\n{i}. " in mail
        for text in (tex, mail):
            assert a["email"] in text and DUMMY["name"] in text
            assert "{fee_limit}" not in text and "[YOUR" not in text
        assert "**" not in mail and "`" not in mail, "markup leaked into the plain-text email"


def test_tex_escaping():
    assert brr.to_tex("$25 & 100% #1 a_b") == r"\$25 \& 100\% \#1 a\_b"
    assert brr.to_tex("**bold** and *it*") == r"\textbf{bold} and \emph{it}"
    assert brr.to_text("**bold** `f_x.pdf` *it*") == "bold f_x.pdf it"


def test_unfilled_requester_is_refused():
    with pytest.raises(SystemExit):
        brr.load_requester(ROOT / "docs" / "records-requests" / "requester.example.yaml")


def test_personal_details_never_tracked():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "private/" in ignore, "private/ (requester details, built letters) must stay gitignored"
    for p in (ROOT / "docs" / "records-requests").glob("*.md"):
        assert "[YOUR NAME]" in p.read_text(encoding="utf-8"), f"{p.name}: public text should carry blanks"


# ---------------------------------------------------------------- legal response clock (RCW 42.56.520, RCW 1.16.050)

def test_wa_legal_holidays_follow_rcw_1_16_050():
    from datetime import date
    h26 = brr.wa_legal_holidays(2026)
    assert {date(2026, 11, 11), date(2026, 11, 26), date(2026, 11, 27), date(2026, 1, 19)} <= h26
    assert date(2026, 7, 3) in h26 and date(2026, 7, 4) not in h26      # Saturday holiday -> preceding Friday
    h27 = brr.wa_legal_holidays(2027)
    assert date(2027, 7, 5) in h27                                     # Sunday holiday -> following Monday
    assert date(2027, 12, 24) in h27                                   # Christmas 2027 is a Saturday
    assert len(h26) == 11


def test_response_window_skips_weekends_and_holidays():
    from datetime import date
    sent = brr.parse_at("2026-11-04T14:30:00-08:00")
    assert brr.response_window(sent) == [date(2026, 11, d) for d in (5, 6, 9, 10, 12)]   # Nov 11 = Veterans Day
    thanksgiving_week = brr.response_window(brr.parse_at("2026-11-25T10:00:00-08:00"))
    assert thanksgiving_week[0] == date(2026, 11, 30) and thanksgiving_week[-1] == date(2026, 12, 4)


@pytest.mark.parametrize("req", REQUESTS, ids=lambda r: r["id"])
def test_sent_requests_show_status_and_due_date(req):
    md = brr.md_path(req).read_text(encoding="utf-8")
    for a in req["agencies"]:
        st = brr.agency_status(a)
        if st is None:
            continue
        assert [e["at"] for e in a["log"]] == sorted(e["at"] for e in a["log"]), f"{a['id']}: log out of order"
        assert brr.day_label(st["due"]) in md, f"{a['id']}: due date missing from the .md status column"
