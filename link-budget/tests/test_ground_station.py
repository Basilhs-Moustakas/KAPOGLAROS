import unittest

from astropy import units as u
from astropy.tests.helper import assert_quantity_allclose
from pycraf import conversions as cnv

from linkbudget.antenna import Antenna
from linkbudget.ground_station import GroundStation
from linkbudget.receiver import DownlinkReceiver
from linkbudget.transmitter import UplinkTransmitter


class GSTestCases(unittest.TestCase):

    def test_gs_transmitter(self):
        utransmitter = UplinkTransmitter(13 * u.W, .155 * cnv.dB, 4, 1 * cnv.dB, .7 * cnv.dB, 0 * cnv.dB)
        assert_quantity_allclose(utransmitter.total_line_losses, 2.06 * cnv.dB, rtol=1e-2)
        assert_quantity_allclose(utransmitter.delivered_power, 9.08 * cnv.dB_W, rtol=1e-2)

    def test_gs_receiver(self):
        dreceiver = DownlinkReceiver((0.23 + 0.0276 + 0.0276) * cnv.dB, 1.5 * cnv.dB, 0 * cnv.dB, 4, 154 * u.K,
                                     290 * u.K, 28 * u.K,
                                     22.5 * cnv.dB, 0.1 * cnv.dB, 1000 * u.K)
        assert_quantity_allclose(dreceiver.total_in_line_losses, 1.985 * cnv.dB, rtol=1e-2)
        assert_quantity_allclose(dreceiver.system_noise_temperature, 238.4 * u.K, rtol=1e-2)

    def test_ground_station(self):
        gs_antenna = Antenna(12 * cnv.dB)
        utransmitter = UplinkTransmitter(13 * u.W, .155 * cnv.dB, 4, 1 * cnv.dB, .7 * cnv.dB, 0 * cnv.dB)
        dreceiver = DownlinkReceiver((0.23 + 0.0276 + 0.0276) * cnv.dB, 1.5 * cnv.dB, 0 * cnv.dB, 4, 154 * u.K,
                                     290 * u.K, 28 * u.K,
                                     22.5 * cnv.dB, 0.1 * cnv.dB, 1000 * u.K)
        gs = GroundStation(gs_antenna, 0 * cnv.dB, dreceiver, utransmitter, 380 * u.km)
        assert_quantity_allclose(gs.figure_of_merit, -13.75 * u.dB(1 / u.K), rtol=1e-2)
