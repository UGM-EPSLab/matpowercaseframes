from matpower import path_matpower

from matpowercaseframes import CaseFrames

"""
    pytest -n auto -rA --cov-report term --cov=matpowercaseframes tests/
"""


def test_case9():
    CASE_NAME = 'case9.m'
    CaseFrames(CASE_NAME)


def test_case4_dist():
    CASE_NAME = 'case4_dist.m'
    CaseFrames(CASE_NAME)


def test_case118():
    CASE_NAME = 'case118.m'
    CaseFrames(CASE_NAME)


def test_t_case9_dcline():
    CASE_NAME = f"{path_matpower}/lib/t/t_case9_dcline.m"
    CaseFrames(CASE_NAME)
