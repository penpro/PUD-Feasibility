# Kitsap Public Power Feasibility Study: project memory

## STOP: check before these operations
| Operation | Rule |
|---|---|
| Git commit/push | Only when explicitly asked. The repo is PUBLIC (github.com/penpro/PUD-Feasibility). |
| Editing anything in `data/raw/` | Never. Raw files are byte-for-byte downloads with SHA-256s in `MANIFEST.sha256`. |
| Adding a number to the model | Only via `model/config.yaml` with label/unit/source/as_of (+ note). `load_config()` enforces it. |
| Hand-editing `modules/*/results.md` or `data/SOURCES.md` | Never: both are generated. Edit config/sources.yaml and rerun. |
| Copyrighted sources (news, commercial sites) | Link in `data/sources.yaml` with `archive_note`; never commit copies. |
| Framing | Neutral: "what would it cost / what would rates be", never "vote yes/no". Test PSE's objections; do not dismiss them. |

## What this is
Independent, open-source feasibility study of KPUD taking over PSE's electric service in Kitsap County.
Seven modules (load, power supply, acquisition, financing, operations, rates, solar/DER). The pillar
that defines "correct": every number is labeled VERIFIED / ESTIMATE / UNVERIFIED / ASSUMPTION, cited, dated, and ranged.

## How to run / verify
- Install: `pip install -r requirements.txt` (pandas, openpyxl, PyYAML, pytest)
- Sources: `python scripts/sources.py build|verify`
- Load model: `python -m model.load` → `data/processed/load/`, `modules/01_load/results.md`
- Election: `python scripts/fetch_election_results.py` (then `sources.py build`)
- Tests: `python -m pytest -q`. Verify by reading the regenerated results.md, not just test passes.

## House rules (inherited, see D:\ClaudeMaster\CLAUDE_BIBLE.md)
Verify by using the artifact. Fix patterns, not symptoms. Check existing tools (bible §6) before building.
Honest verdicts. Decisive on small calls, surface true forks. Local/free/offline by default.

## Earned rules (append as they're learned here)
- 2026-11-04: Third-party "county consumption" figures can be state per-capita × population (FindEnergy's
  11.66 MWh is identical on every WA county page). Check for this before using any aggregator number.
- 2026-11-04: The 2022 county GHG inventory publishes emissions only and does not name its PSE factor.
  Back-calculated kWh swings about ±20% with factor choice. Always show the full factor matrix.
- 2026-11-04: `.gitattributes` has `data/raw/** -text`. Without it, `text=auto` rewrites line endings
  in raw HTML and breaks the hashes on clone.
- 2026-11-04: Run Python that reads downloaded files with `-P` (not `-I`: `-I` hides user site-packages
  such as pandas and fitz on this machine).
