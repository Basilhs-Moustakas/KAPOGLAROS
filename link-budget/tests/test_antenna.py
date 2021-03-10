import unittest

import numpy as np
from astropy import units as u
from astropy.tests.helper import assert_quantity_allclose
from pycraf import conversions as cnv

from linkbudget.antenna import AntennaMeasured, AntennaHelical, AntennaParabolicReflector


class AntennaTestCases(unittest.TestCase):

    def test_antenna_measured(self):
        f = lambda t, p: 3 * np.sin(t) * np.cos(p) ** 2
        # radiation pattern
        rad_pat = np.empty([100, 100])
        # fill the array
        for i, theta in enumerate(np.linspace(-np.pi / 2, np.pi / 2, 100)):
            for j, phi in enumerate(np.linspace(-np.pi, np.pi, 100)):
                rad_pat[i][j] = f(theta, phi)
        antenna = AntennaMeasured(rad_pat, 1)

        self.assertAlmostEqual(antenna.total_radiated_power, 14.8041559, 6)
        self.assertAlmostEqual(antenna.mean_radiation_intensity, antenna.total_radiated_power / (4 * np.pi))
        self.assertAlmostEqual(antenna.directivity(np.pi / 2, np.pi / 2), 0.001922, 6)
        assert_quantity_allclose(antenna.gain, 2.5465222 * cnv.dB)

    def test_antenna_helical(self):
        antenna = AntennaHelical(0.1249 * u.m, 10, (0.25 * 0.1249) * u.m, 0.1249 * u.m)

        assert_quantity_allclose(antenna.diameter, 0.03975690478435546 * u.m)
        assert_quantity_allclose(antenna.gain, 15.740312677277188 * cnv.dB)

    def test_antenna_parabolic_reflector(self):
        antenna = AntennaParabolicReflector(1 * u.m, 0.1249 * u.m, 0.7)

        assert_quantity_allclose(antenna.gain, 26.462729086542534 * cnv.dB)