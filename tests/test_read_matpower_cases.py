import warnings

import numpy as np
import pandas as pd
from matpower import path_matpower, start_instance

from matpowercaseframes import CaseFrames, ReservesFrames, xGenDataTableFrames
from matpowercaseframes.testing import assert_frames_struct_equal

"""
    pytest -n auto -rA --cov-report term --cov=matpowercaseframes tests/
"""


def test_case9():
    CASE_NAME = "case9.m"
    cf = CaseFrames(CASE_NAME)
    cols = pd.Index(["MODEL", "STARTUP", "SHUTDOWN", "NCOST", "C2", "C1", "C0"])
    assert cf.gencost.columns.equals(cols)


def test_case4_dist():
    CASE_NAME = "case4_dist.m"
    CaseFrames(CASE_NAME)


def test_case118():
    m = start_instance()

    CASE_NAME = "case118.m"
    cf = CaseFrames(CASE_NAME)
    cf_lc = CaseFrames(CASE_NAME, load_case_engine=m)
    mpc = m.loadcase(CASE_NAME)
    cf_mpc = CaseFrames(mpc)

    cf.infer_numpy()
    cf_lc.infer_numpy()
    cf_mpc.infer_numpy()

    mpc = m.runpf(cf.to_mpc(), verbose=False)
    _ = CaseFrames(mpc)

    m.exit()

    assert_frames_struct_equal(cf, cf_lc)
    assert_frames_struct_equal(cf, cf_mpc)


def test_case_RTS_GMLC():
    # NOTE: case with gencost piecewise linear
    m = start_instance()

    # TODO: test read without load_case_engine
    CASE_NAME = "case_RTS_GMLC.m"
    cf = CaseFrames(CASE_NAME)
    cf_lc = CaseFrames(CASE_NAME, load_case_engine=m)

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", category=RuntimeWarning, message=".*invalid value.*"
        )
        cf.infer_numpy()
        cf_lc.infer_numpy()

    cols = pd.Index(
        [
            "MODEL",
            "STARTUP",
            "SHUTDOWN",
            "NCOST",
            "X1",
            "Y1",
            "X2",
            "Y2",
            "X3",
            "Y3",
            "X4",
            "Y4",
        ]
    )
    assert cf.gencost.columns.equals(cols)
    assert cf_lc.gencost.columns.equals(cols)

    assert_frames_struct_equal(cf, cf_lc)

    m.exit()


def test_t_case9_dcline():
    CASE_NAME = f"{path_matpower}/lib/t/t_case9_dcline.m"
    CaseFrames(CASE_NAME)


def test_loadcase_case16am():
    # NOTE: case with code inside .m file
    m = start_instance()
    CASE_NAME = "case16am.m"
    CaseFrames(CASE_NAME, load_case_engine=m)
    m.exit()


def test_read_without_ext():
    CASE_NAME = "case9.m"
    cf = CaseFrames(CASE_NAME)

    CASE_NAME = "case9"
    cf_no_ext = CaseFrames(CASE_NAME)

    assert_frames_struct_equal(cf, cf_no_ext)


def test_read_allow_any_keys():
    CASE_NAME = "data/case9_load.m"
    cf = CaseFrames(CASE_NAME)
    assert "load" not in cf.attributes

    cf = CaseFrames(CASE_NAME, allow_any_keys=True)
    assert "load" in cf.attributes


def test_read_case_reserve():
    m = start_instance()
    CASE_NAME = "data/ex_case3a.m"
    cf = CaseFrames(CASE_NAME, load_case_engine=m)

    assert "reserves" in cf.attributes
    assert hasattr(cf, "reserves")

    assert isinstance(cf.reserves, ReservesFrames)

    assert "zones" in cf.reserves.attributes
    assert isinstance(cf.reserves.zones, pd.DataFrame)
    assert cf.reserves.zones.index.name == "zone"
    assert cf.reserves.zones.columns.name == "gen"
    assert cf.reserves.zones.shape == (cf.reserves.req.shape[0], cf.gen.shape[0])

    assert "req" in cf.reserves.attributes
    assert isinstance(cf.reserves.req, pd.DataFrame)
    assert cf.reserves.req.index.name == "zone"
    assert "PREQ" in cf.reserves.req.columns

    assert isinstance(cf.reserves.cost, pd.DataFrame)
    assert "C1" in cf.reserves.cost.columns
    assert cf.reserves.cost.index.name == "gen"

    assert isinstance(cf.reserves.qty, pd.DataFrame)
    assert "PQTY" in cf.reserves.qty.columns
    assert cf.reserves.qty.index.name == "gen"

    for attr in ["zones", "req", "cost", "qty"]:
        assert attr in cf.reserves.attributes

    cf2 = CaseFrames(cf.to_mpc())
    assert_frames_struct_equal(cf, cf2)

    cf.reset_index()
    assert cf.reserves.zones.index.name == "zone"
    assert cf.reserves.zones.columns.name == "gen"
    assert cf.reserves.zones.shape == (cf.reserves.req.shape[0], cf.gen.shape[0])
    assert "C1" in cf.reserves.cost.columns
    assert cf.reserves.cost.index.name == "gen"
    for idx in cf.reserves.cost.index:
        assert idx in cf.gen.index
    assert "PQTY" in cf.reserves.qty.columns
    assert cf.reserves.qty.index.equals(cf.reserves.cost.index)

    m.exit()


def test_read_xgd_table():
    """Test reading and using xGenDataTableFrames."""
    m = start_instance()

    # Load case and xGenDataTable from file
    CASE_NAME = "data/ex_case3a.m"
    cf = CaseFrames(CASE_NAME, load_case_engine=m)

    xgd_table_file = "ex_xgd_uc.m"
    fields = {"colnames", "data"}
    args = cf.to_mpc()

    # Load xGenDataTable using MATPOWER
    # NOTE: loadgenericdata not yet support absolute path
    xgdt = m.loadgenericdata(xgd_table_file, "struct", fields, "xgd_table", args)

    # Create xGenDataTableFrames
    xgdtf = xGenDataTableFrames(
        data=xgdt.data, colnames=xgdt.colnames, index=cf.gen.index
    )

    # Test basic attributes
    assert hasattr(xgdtf, "table")
    assert isinstance(xgdtf.table, pd.DataFrame)
    assert xgdtf.table.index.equals(cf.gen.index)

    # Test properties
    assert xgdtf.colnames.shape[0] == 1  # Should be 2D with one row
    assert xgdtf.data.shape == xgdtf.table.shape
    assert len(xgdtf) == len(cf.gen)

    # Test DataFrame-like behavior
    first_col = xgdtf.table.columns[0]
    assert xgdtf[first_col].equals(xgdtf.table[first_col])

    # Test iteration
    cols_from_iter = list(xgdtf)
    assert cols_from_iter == list(xgdtf.table.columns)

    # Test to_dict and to_mpc
    xgdtf_dict = xgdtf.to_dict()
    assert "colnames" in xgdtf_dict
    assert "data" in xgdtf_dict
    np.testing.assert_array_equal(xgdtf_dict["colnames"], xgdtf.colnames)
    np.testing.assert_array_equal(xgdtf_dict["data"], xgdtf.data)

    m.exit()
