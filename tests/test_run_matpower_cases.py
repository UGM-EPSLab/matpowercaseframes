from matpower import start_instance

from matpowercaseframes import CaseFrames

"""
    pytest -n auto -rA --cov-report term --cov=matpowercaseframes tests/
"""


def test_case9():
    CASE_NAME = "case9.m"
    cf = CaseFrames(CASE_NAME)
    mpc = cf.to_dict()

    m = start_instance()
    m.runpf(mpc)
