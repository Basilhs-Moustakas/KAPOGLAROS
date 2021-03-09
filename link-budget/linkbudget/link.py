from astropy import units as u
from numpy import log10, cos
from pycraf import conversions as cnv

from linkbudget.utils import slant_range


class Link:
    # TODO: Proper implementation of losses and modulation
    def __init__(self, ground_station, spacecraft, freq, elev_angle, additional_losses, ber,
                 allowed_ber, mod_loss, eb_to_no):
        self.ground_station = ground_station
        self.spacecraft = spacecraft
        self.freq = freq.to(u.MHz)
        self.elev_angle = elev_angle.to(u.deg)
        self.additional_losses = additional_losses.to(cnv.dB)
        self.ber = ber
        self.allowed_ber = allowed_ber
        self.mod_loss = mod_loss.to(cnv.dB)
        self.eb_to_no = eb_to_no.to(cnv.dB)

    @property
    def slant_range(self):
        """Slant range"""
        return slant_range(self.spacecraft.sc_altitude, self.ground_station.gs_altitude, self.elev_angle)

    @property
    def path_loss(self):
        c0 = 299792458 * u.m / u.s
        l = c0 / self.freq
        return (21.9842 + 20 * log10(self.slant_range / l)) * u.dB

    @classmethod
    def polarization_loss(cls, var_rw, var_ra, var_theta):
        """
        Described in ITU-R P.341-5
        :float var_rw: Voltage Axial Ratio of the radio wave
        :float var_ra: Voltage Axial Ratio of the receiving antenna
        :astropy.units.Unit var_theta: Tilt angle between the ellipses of the radio wave and antenna polarization
        """
        return -1 * (0.5 + (4 * var_rw * var_ra + (var_rw ** 2 - 1) * (var_ra ** 2 - 1) * cos(2 * var_theta)) / (
                2 * (var_rw ** 2 + 1) * (var_ra ** 2 + 1))).to(cnv.dB)


class Downlink(Link):
    def __init__(self, ground_station, spacecraft, freq, elev_angle, additional_losses, ber,
                 allowed_ber, mod_loss, eb_to_no):
        """
        :~linkbudget.ground_station.GroundStation ground_station: ground station object
        :~linkbudget.spacecraft.Spacecraft spacecraft: spacecraft object
        :~astropy.units.Unit freq: operating frequency
        :~astropy.units.Unit elev_angle: elevation angle
        :~astropy.units.Unit additional_losses: additional losses (excluding path loss and pointing loss)
        :~astropy.units.Unit ber: target Bit Error Rate
        :~astropy.units.Unit allowed_ber: maximum allowed BER
        :~astropy.units.Unit mod_loss: estimated modulation implementation loss
        :~astropy.units.Unit tm_system_eb_to_no: Telemetry System required Eb/no
        :~astropy.units.Unit eb_to_no: energy per bit to noise density
        """
        super().__init__(ground_station, spacecraft, freq, elev_angle, additional_losses, ber,
                         allowed_ber, mod_loss, eb_to_no)

    @property
    def isotropic_signal_level_gs(self):
        """Signal level that would be received at an isotropic antenna on the ground station"""
        return self.spacecraft.spacecraft_eirp - self.total_losses

    @property
    def s_to_no(self):
        """Signal-to-Noise Power Density"""
        return self.isotropic_signal_level_gs - self.spacecraft.pointing_loss + 228.599 * u.dB(
            u.W / u.K / u.Hz) + self.ground_station.figure_of_merit

    @property
    def system_eb_to_no(self):
        """Required Eb/no"""
        return self.s_to_no - 10 * log10(self.ber) * u.dB(u.Hz)

    @property
    def link_margin(self):
        return self.system_eb_to_no - self.eb_to_no - self.mod_loss

    @property
    def total_losses(self):
        return self.additional_losses + self.path_loss + self.ground_station.pointing_loss


class Uplink(Link):

    def __init__(self, ground_station, spacecraft, freq, elev_angle, additional_losses, ber,
                 allowed_ber, mod_loss, eb_to_no):
        """
        :~linkbudget.ground_station.GroundStation ground_station: ground station object
        :~linkbudget.spacecraft.Spacecraft spacecraft: spacecraft object
        :~astropy.units.Unit freq: operating frequency
        :~astropy.units.Unit elev_angle: elevation angle
        :~astropy.units.Unit additional_losses: additional path losses (excluding path loss and pointing loss)
        :~astropy.units.Unit ber: target Bit Error Rate
        :~astropy.units.Unit allowed_ber: maximum allowed BER
        :~astropy.units.Unit mod_loss: estimated modulation implementation loss
        :~astropy.units.Unit eb_to_no: required energy per bit to noise density
        """
        super().__init__(ground_station, spacecraft, freq, elev_angle, additional_losses, ber,
                         allowed_ber, mod_loss, eb_to_no)

    @property
    def isotropic_signal_level_sc(self):
        """Signal level that would be received at an isotropic antenna on the spacecraft"""
        return self.ground_station.ground_station_eirp - self.total_losses

    @property
    def s_to_no(self):
        """Signal-to-Noise Power Density"""
        return self.isotropic_signal_level_sc - self.spacecraft.pointing_loss + 228.6 * u.dB(
            u.W / u.K / u.Hz) + self.spacecraft.figure_of_merit

    @property
    def system_eb_to_no(self):
        """Required Eb/no"""
        return self.s_to_no - 10 * log10(self.ber) * u.dB(u.Hz)

    @property
    def link_margin(self):
        return self.system_eb_to_no - self.eb_to_no - self.mod_loss

    @property
    def total_losses(self):
        return self.additional_losses + self.path_loss + self.spacecraft.pointing_loss
