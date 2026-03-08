import pytest
from matpower import run_matlab_cmd, start_instance

from matpowercaseframes import CaseFrames

try:
    import matlab.engine  # noqa: F401

    MATLAB_AVAILABLE = True
except ImportError:
    MATLAB_AVAILABLE = False

"""
    pytest -n auto -rA --cov-report term --cov=matpowercaseframes tests/

    case9          : default MATPOWER case, run power flow via to_dict()
    case_RTS_GMLC  : piecewise linear gencost (TYPE=1) and contains bus_name,
                     run power flow via to_mpc(backend="matlab")
"""


def test_case9():
    """Load case9, convert to dict, and run power flow with octave engine."""
    CASE_NAME = "case9.m"
    cf = CaseFrames(CASE_NAME)
    mpc = cf.to_dict()

    m = start_instance()
    m.runpf(mpc)


@pytest.mark.skipif(not MATLAB_AVAILABLE, reason="MATLAB not available")
def test_case_RTS_GMLC_matlab():
    """Load case_RTS_GMLC (has bus_name), convert via to_mpc(backend="matlab"),
    and run power flow with matlab engine."""
    CASE_NAME = "case_RTS_GMLC.m"

    m = start_instance(engine="matlab")

    cf = CaseFrames(CASE_NAME, load_case_engine=m)
    mpc = cf.to_mpc(backend="matlab")
    _ = run_matlab_cmd("runpf(mpc)", m=m, mpc=mpc)

    m.exit()
