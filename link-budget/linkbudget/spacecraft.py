from astropy import units as u


class Spacecraft:
    def __init__(self, sc_antenna, sc_antenna_pointing_loss, sc_receiver, sc_transmitter, sc_altitude):
        """
        :~linkbudget.antenna.Antenna sc_antenna: spacecraft antenna
        :~linkbudget.antenna.Antenna gs_antenna_pointing_loss: spacecraft antenna's pointing loss
        :~linkbudgets.receiver.UplinkReceiver sc_receiver: spacecraft downlink receiver
        :~linkbudgets.transmitter.DownlinkTransmitter sc_transmitter: spacecraft uplink transmitter
        :~astropy.units.Unit sc_altitude: spacecraft altitude
        """
        self.sc_antenna = sc_antenna
        self.sc_antenna_pointing_loss = sc_antenna_pointing_loss
        self.sc_receiver = sc_receiver
        self.sc_transmitter = sc_transmitter
        self.sc_altitude = sc_altitude.to(u.km)
        self.pointing_loss = 0 * u.dB

    @property
    def figure_of_merit(self):
        return 2.0*u.dB - self.sc_receiver.total_in_line_losses - self.sc_receiver.system_noise_temperature.to(
            u.dB(u.K))

    # TODO: Handle pointing losses in a more intuitive way

    @property
    def spacecraft_eirp(self):
        """Spacecraft Effective Radiated Power"""
        return self.sc_transmitter.power_output - self.sc_transmitter.total_line_losses + 2.873 * u.dB
