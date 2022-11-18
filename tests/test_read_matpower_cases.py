from matpowercaseframes import CaseFrames
from matpowercaseframes.idx import BUS_I, BUS_TYPE

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
