"""Load module: arithmetic, internal consistency, and parser cross-checks."""
import pytest

from model import eia861
from model.common import CASES, load_config
from model.load import run


@pytest.fixture(scope="module")
def r():
    return run()


@pytest.fixture(scope="module")
def cfg():
    return load_config()


def test_findenergy_is_statewide_per_capita_times_population(r):
    a = r["a"]
    assert a["is_state_average_scaled"]
    assert a["state_pc_x_county_pop_mwh"] == pytest.approx(a["total_mwh"], rel=0.001)


def test_backcalc_central_arithmetic(r):
    # 828,336 tCO2e / (109.25 gCO2e/MJ * 3600 MJ/MWh / 1e6 g/t)
    assert r["b"].loc["central", "total_mwh_2022"] == pytest.approx(828336 / (109.25 * 0.0036), abs=1)


def test_backcalc_sectors_sum(r):
    b = r["b"]
    assert (b.residential_mwh + b.commercial_mwh + b.industrial_mwh).round(3).equals(b.total_mwh_2022.round(3))


def test_reconciled_cases_are_ordered(r):
    e = r["recon"]["retail_mwh"]
    assert e["stress_low"] <= e["low"] <= e["central"] <= e["high"] <= e["stress_high"]


def test_method_b_range_inside_method_c_stress(r):
    b, c = r["b"], r["c"]
    assert c.loc["low", "total_mwh"] <= b.loc["low", "total_mwh_base"]
    assert b.loc["high", "total_mwh_base"] <= c.loc["high", "total_mwh"]


def test_peaks_are_ordered_and_exceed_average(r):
    pk = r["peak"]
    assert pk.loc["low", "peak_mw"] < pk.loc["central", "peak_mw"] < pk.loc["high", "peak_mw"]
    assert (pk["peak_mw"] > pk["avg_mw_system"]).all()


def test_monthly_sums_to_annual(r):
    mon, recon = r["monthly"], r["recon"]
    assert mon["total_mwh"].sum() == pytest.approx(recon.loc["central", "retail_mwh"], rel=1e-9)
    for cls in ("residential", "commercial", "industrial"):
        assert mon[f"{cls}_share"].sum() == pytest.approx(1.0, abs=1e-9)
    # winter-peaking: Dec-Feb above the annual average, Jun and Sep below
    assert (mon.loc[[12, 1, 2], "ratio_to_annual_avg"] > 1).all()
    assert (mon.loc[[6, 9], "ratio_to_annual_avg"] < 1).all()


def test_projection_base_year_equals_reconciled(r, cfg):
    by = cfg["settings"]["base_year"]
    for case in CASES:
        assert r["proj"].loc[(case, by), "retail_mwh"] == pytest.approx(r["recon"].loc[case, "retail_mwh"])
        assert r["proj"].loc[(case, by), "ev_adder_mwh"] == 0


def test_861m_monthly_sums_match_861_annual():
    """Two independent EIA files, two parsers: PSE 2025 residential MWh must agree."""
    monthly_total = eia861.monthly_sales(2025)["RESIDENTIAL|Sales"].sum()
    annual = eia861.benchmarks().loc[eia861.PSE, "res_mwh"]
    assert monthly_total == pytest.approx(annual, rel=0.01)


def test_service_territory_lists_four_kitsap_utilities():
    names = set(eia861.service_territory("Kitsap")["Utility Name"])
    assert names == {"Puget Sound Energy Inc", "Bonneville Power Administration",
                     "Peninsula Light Company", "PUD No 3 of Mason County"}
