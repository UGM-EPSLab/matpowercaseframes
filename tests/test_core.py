
import os
import numpy as np

from matpowercaseframes import CaseFrames
from matpowercaseframes.idx import *

CURDIR = os.path.realpath(os.path.dirname(__file__))

class TestCore:
    @classmethod
    def setup_class(cls):
        cls.path = os.path.join(CURDIR, "data/case9.m")
        cls.cf = CaseFrames(cls.path)

    def test_read_value(self):
        assert self.cf.version == '2'
        assert self.cf.baseMVA == 100

        narr_gencost = np.array([
            [2.000e+00, 1.500e+03, 0.000e+00, 3.000e+00, 1.100e-01, 5.000e+00, 1.500e+02],
            [2.000e+00, 2.000e+03, 0.000e+00, 3.000e+00, 8.500e-02, 1.200e+00, 6.000e+02],
            [2.000e+00, 3.000e+03, 0.000e+00, 3.000e+00, 1.225e-01, 1.000e+00, 3.350e+02]
        ])
        assert np.allclose(self.cf.gencost, narr_gencost)

        narr_bus = np.array([
            [1, 3, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [2, 2, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [3, 2, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [4, 1, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [5, 1, 90, 30, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [6, 1, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [7, 1, 100, 35, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [8, 1, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [9, 1, 125, 50, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9]
        ])
        assert np.allclose(self.cf.bus, narr_bus)
        assert np.allclose(self.cf.bus['BUS_I'], narr_bus[:,BUS_I])
        assert np.allclose(self.cf.bus['BUS_TYPE'], narr_bus[:,BUS_TYPE])

        # TODO:
        # Check all data

    def test_read_case_name(self):
        assert self.cf.name == 'case9'
