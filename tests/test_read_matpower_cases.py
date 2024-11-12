from matpower import path_matpower, start_instance

from matpowercaseframes import CaseFrames

"""
    pytest -n auto -rA --cov-report term --cov=matpowercaseframes tests/
"""


def test_case9():
    CASE_NAME = "case9.m"
    CaseFrames(CASE_NAME)


def test_case4_dist():
    CASE_NAME = "case4_dist.m"
    CaseFrames(CASE_NAME)


def test_case118():
    CASE_NAME = "case118.m"
    CaseFrames(CASE_NAME)


def test_t_case9_dcline():
    CASE_NAME = f"{path_matpower}/lib/t/t_case9_dcline.m"
    CaseFrames(CASE_NAME)


def test_loadcase_case16am():
    m = start_instance()
    CASE_NAME = "case16am.m"
    CaseFrames(CASE_NAME, load_case_engine=m)
    m.exit()


def test_read_without_ext():
    CASE_NAME = "case9"
    CaseFrames(CASE_NAME)


def test_read_allow_any_keys():
    CASE_NAME = "data/case9_load.m"
    cf = CaseFrames(CASE_NAME)
    assert "load" not in cf.attributes

    cf = CaseFrames(CASE_NAME, allow_any_keys=True)
    assert "load" in cf.attributes
