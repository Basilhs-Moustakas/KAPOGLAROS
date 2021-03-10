import unittest

from astropy import units as u
from astropy.tests.helper import assert_quantity_allclose
from pycraf import conversions as cnv

from linkbudget.antenna import Antenna
from linkbudget.ground_station import GroundStation
from linkbudget.link import Downlink, Uplink, Link
from linkbudget.receiver import DownlinkReceiver, UplinkReceiver
from linkbudget.spacecraft import Spacecraft
from linkbudget.transmitter import DownlinkTransmitter, UplinkTransmitter


class LinkTestCases(unittest.TestCase):

    def test_downlink(self):
        # Ground station
        gs_antenna = Antenna(12 * cnv.dB)
        utransmitter = UplinkTransmitter(13 * u.W, .155 * cnv.dB, 4, 1 * cnv.dB, .7 * cnv.dB, 0 * cnv.dB)
        dreceiver = DownlinkReceiver((0.23 + 0.0276 + 0.0276) * cnv.dB, 1.5 * cnv.dB, 0 * cnv.dB, 4, 154 * u.K,
                                     290 * u.K, 28 * u.K,
                                     22.5 * cnv.dB, 0.1 * cnv.dB, 1000 * u.K)
        ground_station = GroundStation(gs_antenna, 0 * cnv.dB, dreceiver, utransmitter, 50 * u.m)

        # Spacecraft
        sc_antenna = Antenna(-1.3 * cnv.dB)
        dtransmitter = DownlinkTransmitter(1.3 * u.W, 0 * cnv.dB, 4, 0 * cnv.dB, 0.5 * cnv.dB, 0.23 * cnv.dB)
        utransmitter = UplinkReceiver((0.08 + 0.04 + 0.04) * cnv.dB, 0.7 * cnv.dB, 0.5 * cnv.dB, 2, 280 * u.K,
                                      280 * u.K, 28 * u.K,
                                      20 * cnv.dB, 0 * u.K)
        spacecraft = Spacecraft(sc_antenna, 0 * cnv.dB, utransmitter, dtransmitter, 380 * u.km)

        # Downlink
        dlink = Downlink(ground_station, spacecraft, 437 * u.MHz, 30 * u.deg, 3.4 * cnv.dB,
                         20000, 1e-6, 1 * cnv.dB, 8 * cnv.dB)
        assert_quantity_allclose(dlink.slant_range, 704.68 * u.km, rtol=1e-2)
        assert_quantity_allclose(dlink.path_loss, 142.22 * u.dB, rtol=1e-2)
        assert_quantity_allclose(dlink.isotropic_signal_level_gs, -146.708 * cnv.dB_W, rtol=1e-2)
        self.assertLess(abs((dlink.s_to_no - 68.15 * u.dB(u.Hz)).value), 1e-1)
        self.assertLess(abs((dlink.system_eb_to_no - 25.14 * u.dB(u.Hz)).value), 1e-1)
        self.assertLess(abs((dlink.link_margin - 16.14 * cnv.dB).value), 1e-1)

    def test_uplink(self):
        # Ground station
        gs_antenna = Antenna(12 * cnv.dB)
        utransmitter = UplinkTransmitter(13 * u.W, .155 * cnv.dB, 4, 1 * cnv.dB, .7 * cnv.dB, 0 * cnv.dB)
        dreceiver = DownlinkReceiver((0.23 + 0.0276 + 0.0276) * cnv.dB, 1.5 * cnv.dB, 0 * cnv.dB, 4, 154 * u.K,
                                     290 * u.K, 28 * u.K,
                                     22.5 * cnv.dB, 0.1 * cnv.dB, 1000 * u.K)
        ground_station = GroundStation(gs_antenna, 0 * cnv.dB, dreceiver, utransmitter, 50 * u.m)

        # Spacecraft
        sc_antenna = Antenna(-1.3 * cnv.dB)
        dtransmitter = DownlinkTransmitter(1.3 * u.W, 0 * cnv.dB, 4, 0 * cnv.dB, 0.5 * cnv.dB, 0.23 * cnv.dB)
        utransmitter = UplinkReceiver((0.08 + 0.04 + 0.04) * cnv.dB, 0.7 * cnv.dB, 0.5 * cnv.dB, 2, 280 * u.K,
                                      280 * u.K, 28 * u.K,
                                      20 * cnv.dB, 0 * u.K)
        spacecraft = Spacecraft(sc_antenna, 0 * cnv.dB, utransmitter, dtransmitter, 380 * u.km)

        # Uplink
        ulink = Uplink(ground_station, spacecraft, 437 * u.MHz, 30 * u.deg, 3.4 * cnv.dB, 20000,
                       1e-6, 1 * cnv.dB, 8 * cnv.dB)

        assert_quantity_allclose(ulink.slant_range, 704.68 * u.km, rtol=1e-2)
        assert_quantity_allclose(ulink.path_loss, 142.22 * u.dB, rtol=1e-2)
        assert_quantity_allclose(ulink.isotropic_signal_level_sc, -124.5 * cnv.dB_W, rtol=1e-2)
        self.assertLess(abs((ulink.s_to_no - 76.4 * u.dB(u.Hz)).value), 1e-1)
        self.assertLess(abs((ulink.system_eb_to_no - 33.4 * u.dB(u.Hz)).value), 1e-1)
        self.assertLess(abs((ulink.link_margin - 24.4 * cnv.dB).value), 1e-1)

    def test_polarization_loss(self):
        assert_quantity_allclose(Link.polarization_loss(1.4125, 1.4125, 1.5707 * u.rad), 0.508 * u.dB, rtol=1e-2)
