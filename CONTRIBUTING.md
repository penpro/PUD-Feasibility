# Contributing

This study is only useful if people on every side of the debate can check it. Challenges are as
welcome as data.

## Three ways to contribute

### 1. Submit data

Open an issue using the **Data submission** template, or a pull request that:

1. Adds the file **unmodified** under `data/raw/<short_source_name>/`. Do not clean, convert or rename
   the contents. If processing is needed, write code in `model/` that reads the raw file.
2. Registers it in `data/sources.yaml` with a new ID (`S0nn`), publisher, URL, access date, kind
   (primary / secondary / third-party / advocacy) and notes saying which numbers it supports and where
   (page or table).
3. Runs `python scripts/sources.py build` (updates the manifest and `data/SOURCES.md`).

Copyrighted material (news articles, commercial sites) is cited by link in `sources.yaml` with an
`archive_note`. It is not committed.

### 2. Report a correction

Use the **Correction** template: which number, where it appears, what it should be, and the source.
Corrections that change a result also update `model/config.yaml`. Rerun the model; never hand-edit
generated files (`modules/*/results.md`, `data/SOURCES.md`).

### 3. Challenge an assumption or finding

Use the **Challenge** template. ASSUMPTION-labeled parameters are the first things to challenge. Say what
you think the value should be, why, and what evidence would settle it. A good challenge can be expressed as
a different `low/central/high` in `model/config.yaml`.

## Rules for every change

- **Every number has a label, unit, source ID and date.** The model refuses to run otherwise.
- **Ranges, not points.** New parameters get `low/central/high` unless the value is a measured fact.
- **Neutral framing.** Describe what a number means. Do not say what anyone should do about it. Present
  claims from all sides, including PSE and KPUD advocates, as claims to be tested.
- **Primary sources win.** Utility filings, UTC dockets, BPA, EIA, state agencies and county records beat
  journalism, which beats aggregators. An advocacy source is primary only for its own operating facts.
- **Report negative results.** If new data moves a number the "wrong" way for anyone, it still goes in.

## Before opening a pull request

```bash
python scripts/sources.py verify
```

```bash
python -m model.load
```

```bash
python -m pytest -q
```

All three must pass, and the regenerated results must be committed along with the change.

## License of contributions

Code contributions are MIT. Documentation and processed-data contributions are CC BY 4.0. By opening a
pull request you agree to license your contribution under those terms.
