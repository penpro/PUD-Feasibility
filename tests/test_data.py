"""Raw data integrity and the election parser."""
import subprocess
import sys

from conftest import ROOT

import fetch_election_results as fer


def test_raw_files_match_manifest():
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "sources.py"), "verify"],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr


def test_election_parser_on_first_snapshot():
    html = (ROOT / "data/raw/election_2026/results_2026-11-03_2002.html").read_bytes().decode("utf-8", "replace")
    rec = fer.parse(html)
    assert rec["run_datetime"] == "2026-11-03T20:02"
    assert rec["official"] is False
    assert (rec["yes"], rec["no"]) == (34935, 53513)
    assert (rec["yes_pct"], rec["no_pct"]) == ("39.50%", "60.50%")
    assert (rec["registered_voters"], rec["ballots_tabulated"]) == (204242, 92136)
    assert (rec["undervotes"], rec["overvotes"]) == (3683, 5)
