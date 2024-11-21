import pandas as pd
from matpower import path_matpower, start_instance
from pandas.testing import assert_frame_equal, assert_index_equal

from matpowercaseframes import CaseFrames

"""
    pytest -n auto -rA --cov-report term --cov=matpowercaseframes tests/
"""


def assert_cf_equal(cf1, cf2):
    for attribute in cf1.attributes:
        df1 = getattr(cf1, attribute)
        df2 = getattr(cf2, attribute)
        if isinstance(df1, pd.DataFrame):
            assert_frame_equal(df1, df2)
        elif isinstance(df1, pd.Index):
            assert_index_equal(df1, df2)
        else:
            try:
                assert df1 == df2
            except ValueError as e:
                print(df1, df2)
                raise ValueError(e)


def test_case9():
    CASE_NAME = "case9.m"
    CaseFrames(CASE_NAME)


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

    assert_cf_equal(cf, cf_lc)
    assert_cf_equal(cf, cf_mpc)


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

    assert_cf_equal(cf, cf_no_ext)


def test_read_allow_any_keys():
    CASE_NAME = "data/case9_load.m"
    cf = CaseFrames(CASE_NAME)
    assert "load" not in cf.attributes

    cf = CaseFrames(CASE_NAME, allow_any_keys=True)
    assert "load" in cf.attributes
