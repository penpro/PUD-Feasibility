"""The config chokepoint: every number has provenance, and EIA-derived numbers match the raw files."""
import pytest

from model import eia861
from model.common import load_config, val, validate
from model.load import EF_MATRIX

TOL = 1e-3


@pytest.fixture(scope="module")
def cfg():
    return load_config()


@pytest.fixture(scope="module")
def bench():
    return eia861.benchmarks()


def test_config_validates(cfg):
    assert cfg["params"]["load"]


def test_validator_rejects_bare_number():
    assert any("bare value" in p for p in validate({"x": {"y": 5}}, set()))


def test_validator_rejects_missing_label_and_unknown_source():
    probs = validate({"x": {"value": 1, "unit": "u", "as_of": 2025, "source": ["S999"]}}, {"S001"})
    assert any("label" in p for p in probs)
    assert any("unknown source" in p for p in probs)


def test_validator_requires_note_on_assumptions():
    probs = validate({"x": {"value": 1, "unit": "u", "as_of": 2025, "source": [], "label": "ASSUMPTION"}}, set())
    assert any("note" in p for p in probs)


def _mid(a, b):
    return (a + b) / 2


PSE, JEFF, MASON = 15500, 59013, 15419


@pytest.mark.parametrize("key,col,low_u,high_u", [
    ("load.bottom_up.residential_mwh_per_customer", "res_mwh_per_customer", PSE, MASON),
    ("load.bottom_up.commercial_mwh_per_customer", "com_mwh_per_customer", JEFF, PSE),
    ("load.losses", "loss_fraction", JEFF, MASON),
    ("load.load_factor", "load_factor", JEFF, PSE),
])
def test_eia_derived_bounds_match_raw(cfg, bench, key, col, low_u, high_u):
    assert val(cfg, key, "low") == pytest.approx(bench.loc[low_u, col], abs=TOL)
    assert val(cfg, key, "high") == pytest.approx(bench.loc[high_u, col], abs=TOL)
    # settings.central_rule: midpoint of PSE system-wide and Jefferson PUD
    assert val(cfg, key, "central") == pytest.approx(_mid(bench.loc[PSE, col], bench.loc[JEFF, col]), abs=TOL)


def test_backcalc_factor_bounds_are_matrix_extremes(cfg):
    vals = [val(cfg, f"load.pse_carbon_intensity.{k}") for _, _, k in EF_MATRIX]
    assert val(cfg, "load.ghg_backcalc_ef", "low") == min(vals)
    assert val(cfg, "load.ghg_backcalc_ef", "high") == max(vals)
    assert val(cfg, "load.ghg_backcalc_ef", "central") == val(cfg, "load.pse_carbon_intensity.ci_2022mix_production_to_consumption")


def test_industrial_uplift_matches_inventory(cfg):
    g = "load.ghg_inventory_2022"
    ratio = val(cfg, f"{g}.electricity_industrial") / (val(cfg, f"{g}.electricity_residential") + val(cfg, f"{g}.electricity_commercial"))
    assert val(cfg, "load.bottom_up.industrial_uplift") == pytest.approx(ratio, abs=1e-6)


def test_pse_2022_ci_components_sum(cfg):
    k = "load.pse_carbon_intensity"
    assert val(cfg, f"{k}.ci_2022mix_total") == pytest.approx(13.34 + val(cfg, f"{k}.ci_2022mix_production_to_consumption"), abs=0.01)
