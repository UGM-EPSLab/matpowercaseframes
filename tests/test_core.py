
import os
import numpy as np

from matpowercaseframes import CaseFrames

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

        # TODO:
        # Check all data

    def test_read_case_name(self):
        assert self.cf.name == 'case9'
