import unittest

from astropy import units as u
from astropy.tests.helper import assert_quantity_allclose
from pycraf import conversions as cnv

from linkbudget.antenna import Antenna
from linkbudget.receiver import UplinkReceiver
from linkbudget.spacecraft import Spacecraft
from linkbudget.transmitter import DownlinkTransmitter


class SCTestCases(unittest.TestCase):

    def test_sc_transmitter(self):
        dtransmitter = DownlinkTransmitter(1.3 * u.W, 0 * cnv.dB, 4, 0 * cnv.dB, 0.5 * cnv.dB, 0.23 * cnv.dB)
        assert_quantity_allclose(dtransmitter.delivered_power, 0.209433 * cnv.dB_W, rtol=1e-2)
        assert_quantity_allclose(dtransmitter.total_line_losses, 0.93 * cnv.dB, rtol=1e-2)

    def test_sc_receiver(self):
        ureceiver = UplinkReceiver((0.08 + 0.04 + 0.04) * cnv.dB, 0.7 * cnv.dB, 0.5 * cnv.dB, 2, 280 * u.K, 280 * u.K,
                                   28 * u.K,
                                   20 * cnv.dB, 0 * u.K)
        assert_quantity_allclose(ureceiver.total_in_line_losses, 1.46 * cnv.dB, rtol=1e-2)
        assert_quantity_allclose(ureceiver.system_noise_temperature, 308 * u.K, rtol=1e-2)

    def test_spacecraft(self):
        sc_antenna = Antenna(-1.3 * cnv.dB)
        dtransmitter = DownlinkTransmitter(1.3 * u.W, 0 * cnv.dB, 4, 0 * cnv.dB, 0.5 * cnv.dB, 0.23 * cnv.dB)
        utransmitter = UplinkReceiver((0.08 + 0.04 + 0.04) * cnv.dB, 0.7 * cnv.dB, 0.5 * cnv.dB, 2, 280 * u.K,
                                      280 * u.K, 28 * u.K,
                                      20 * cnv.dB, 0 * u.K)
        spacecraft = Spacecraft(sc_antenna, 0 * cnv.dB, utransmitter, dtransmitter, 50 * u.m)
        assert_quantity_allclose(spacecraft.figure_of_merit, -27.6 * u.dB(1 / u.K), rtol=1e-1)
