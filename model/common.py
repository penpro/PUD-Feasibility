"""Shared paths, units, and the config chokepoint.

Every number the model uses comes from model/config.yaml through `load_config()`, which
refuses to run if any parameter lacks a provenance label, unit, source, or date. A bare
number with no provenance is a validation error, not a warning.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

import yaml

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
CONFIG_PATH = ROOT / "model" / "config.yaml"
REGISTRY_PATH = ROOT / "data" / "sources.yaml"

LABELS = ("VERIFIED", "ESTIMATE", "UNVERIFIED", "ASSUMPTION")
CASES = ("low", "central", "high")
VALUE_KEYS = {"value", "low", "central", "high", "points"}

HOURS_PER_YEAR = 8760
MJ_PER_MWH = 3600.0


def g_per_mj_to_t_per_mwh(g_per_mj: float) -> float:
    """gCO2e/MJ -> tCO2e/MWh.  x g/MJ * 3600 MJ/MWh / 1e6 g/t."""
    return g_per_mj * MJ_PER_MWH / 1e6


class ConfigError(ValueError):
    pass


def source_ids() -> set[str]:
    reg = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {s["id"] for s in reg["sources"]}


def iter_params(node: Any, path: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], Any]]:
    """Yield (path, node) for every parameter leaf. Non-parameter leaves are yielded too,
    so the validator can reject them."""
    if isinstance(node, dict) and VALUE_KEYS & node.keys():
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from iter_params(v, path + (str(k),))
    else:
        yield path, node


def validate(params: dict, known_sources: set[str]) -> list[str]:
    problems: list[str] = []
    for path, p in iter_params(params):
        name = ".".join(path)
        if not isinstance(p, dict):
            problems.append(f"{name}: bare value {p!r} with no provenance (wrap it with label/unit/source/as_of)")
            continue
        label = p.get("label")
        if label not in LABELS:
            problems.append(f"{name}: label must be one of {LABELS}, got {label!r}")
        for key in ("unit", "as_of"):
            if key not in p:
                problems.append(f"{name}: missing '{key}'")
        src = p.get("source")
        if not isinstance(src, list):
            problems.append(f"{name}: 'source' must be a list of source IDs (may be [] only for ASSUMPTION)")
        else:
            for s in src:
                if s not in known_sources:
                    problems.append(f"{name}: unknown source id {s!r} (add it to data/sources.yaml)")
            if not src and label != "ASSUMPTION":
                problems.append(f"{name}: {label} values must cite at least one source")
        if label in ("ESTIMATE", "ASSUMPTION", "UNVERIFIED") and not p.get("note"):
            problems.append(f"{name}: {label} values need a 'note' explaining the method or doubt")
        if "value" not in p:
            if "points" in p:
                if not isinstance(p["points"], dict) or not p["points"]:
                    problems.append(f"{name}: 'points' must be a non-empty mapping")
            else:
                missing = [c for c in CASES if c not in p]
                if missing:
                    problems.append(f"{name}: range parameter missing {missing}")
    return problems


def load_config(path: Path = CONFIG_PATH) -> dict:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    problems = validate(cfg["params"], source_ids())
    if problems:
        raise ConfigError("model/config.yaml failed validation:\n  " + "\n  ".join(problems))
    return cfg


def param(cfg: dict, dotted: str) -> dict:
    node: Any = cfg["params"]
    for part in dotted.split("."):
        node = node[part]
    return node


def val(cfg: dict, dotted: str, case: str = "central") -> float:
    """Numeric value of a parameter. Point values ignore `case`; ranges return that case."""
    p = param(cfg, dotted)
    if "value" in p:
        return p["value"]
    return p[case]


def ref(cfg: dict, dotted: str) -> str:
    """Short provenance tag for reports, e.g. 'VERIFIED · S006'."""
    p = param(cfg, dotted)
    src = ", ".join(p.get("source") or []) or "modeler judgment"
    return f"{p['label']} · {src}"
