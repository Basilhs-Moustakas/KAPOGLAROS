import unittest

from astropy import units as u
from astropy.tests.helper import assert_quantity_allclose

from linkbudget.utils import slant_range


class UtilsTestCases(unittest.TestCase):

    def test_slant_range(self):
        d = slant_range(380 * u.km, 50 * u.m, 30 * u.deg)
        assert_quantity_allclose(d, 704.68 * u.km, rtol=1e-2)
