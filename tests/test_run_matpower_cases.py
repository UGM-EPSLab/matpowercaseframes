from matpower import start_instance

from matpowercaseframes import CaseFrames

"""
    pytest -n auto -rA --cov-report term --cov=matpowercaseframes tests/

    case9 : default MATPOWER case, run power flow via to_dict()
"""


def test_case9():
    """Load case9, convert to dict, and run power flow with octave engine."""
    CASE_NAME = "case9.m"
    cf = CaseFrames(CASE_NAME)
    mpc = cf.to_dict()

    m = start_instance()
    m.runpf(mpc)
