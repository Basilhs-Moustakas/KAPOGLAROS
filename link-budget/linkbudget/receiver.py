from astropy import units as u
from pycraf import conversions as cnv


# TODO: Temperature approximation calculator
class Receiver:
    def __init__(self, guide_loss, bandpass_filter_insertion_loss, other_in_line_insertion_loss, connectors,
                 sky_temperature, lna_temperature, lna_gain):
        self.guide_loss = guide_loss.to(cnv.dB)
        self.bandpass_filter_insertion_loss = bandpass_filter_insertion_loss.to(cnv.dB)
        self.other_in_line_insertion_loss = other_in_line_insertion_loss.to(cnv.dB)
        self.connectors = connectors
        self.sky_temperature = sky_temperature.to(u.K)
        self.lna_temperature = lna_temperature.to(u.K)
        self.lna_gain = lna_gain.to(cnv.dB)

    @property
    def total_in_line_losses(self):
        """Total in-line losses"""
        return self.guide_loss + self.bandpass_filter_insertion_loss + self.other_in_line_insertion_loss \
               + self.connectors * 0.05 * cnv.dB


class UplinkReceiver(Receiver):
    def __init__(self, guide_loss, bandpass_filter_insertion_loss, other_in_line_insertion_loss, connectors,
                 sky_temperature, spacecraft_temperature, lna_temperature, lna_gain, second_stage_temperature):
        """
        :~astropy.units.Unit guide_loss: Total guide loss
        :~astropy.units.Unit bandpass_filter_insertion_loss: Bandpass filter insertion loss
        :~astropy.units.Unit other_in_line_insertion_loss: Other in-line losses
        :int connectors: number of connectors
        :~astropy.units.Unit sky_temperature: The sky temperature on the spacecraft's antenna
        :~astropy.units.Unit spacecraft_temperature: Spacecraft temperature
        :~astropy.units.Unit lna_temperature: LNA temperature
        :~astropy.units.Unit lna_gain: LNA gain
        :~astropy.units.Unit second_stage_temperature: Second stage temperature
        """
        super().__init__(guide_loss, bandpass_filter_insertion_loss, other_in_line_insertion_loss, connectors,
                         sky_temperature, lna_temperature, lna_gain)
        self.second_stage_temperature = second_stage_temperature.to(u.K)
        self.spacecraft_temperature = spacecraft_temperature.to(u.K)

    @property
    def system_noise_temperature(self):
        """System Noise Temperature"""
        a = 1 / (self.total_in_line_losses).to(u.dimensionless_unscaled)
        g = self.lna_gain.to(u.dimensionless_unscaled)
        return self.sky_temperature * a + self.spacecraft_temperature * (1 - a) + self.lna_temperature
        + self.second_stage_temperature / g


class DownlinkReceiver(Receiver):
    def __init__(self, guide_loss, bandpass_filter_insertion_loss, other_in_line_insertion_loss, connectors,
                 sky_temperature, ground_station_temperature, lna_temperature, lna_gain, waveguide_losses,
                 comms_receiver_front_end_temperature):
        """
        :~astropy.units.Unit guide_loss: Total guide loss
        :~astropy.units.Unit bandpass_filter_insertion_loss: Bandpass filter insertion loss
        :~astropy.units.Unit other_in_line_insertion_loss: Other in-line losses
        :int connectors: number of connectors
        :~astropy.units.Unit sky_temperature: The sky temperature on the ground stations's antenna
        :~astropy.units.Unit ground_station_temperature: Ground station feedline temperature
        :~astropy.units.Unit lna_temperature: LNA temperature
        :~astropy.units.Unit lna_gain: LNA gain
        :~astropy.units.Unit second_stage_temperature: Second stage temperature
        :~astropy.units.Unit waveguide_losses: Waveguide losses (LNA to Comms Receiver)
        """
        super().__init__(guide_loss, bandpass_filter_insertion_loss, other_in_line_insertion_loss, connectors,
                         sky_temperature, lna_temperature, lna_gain)
        self.waveguide_losses = waveguide_losses
        self.ground_station_temperature = ground_station_temperature.to(u.K)
        self.comms_receiver_front_end_temperature = comms_receiver_front_end_temperature.to(u.K)

    @property
    def system_noise_temperature(self):
        """System Noise Temperature"""
        a = 1 / self.total_in_line_losses.to(u.dimensionless_unscaled)
        g = self.lna_gain.to(u.dimensionless_unscaled)
        return self.sky_temperature * a + self.ground_station_temperature * (1 - a) + self.lna_temperature + 10 ** (
                a / 10) * self.comms_receiver_front_end_temperature / g
