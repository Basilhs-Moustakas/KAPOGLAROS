from astropy import units as u


class GroundStation:
    def __init__(self, gs_antenna, gs_antenna_pointing_loss, gs_receiver, gs_transmitter, gs_altitude):
        """
        :~linkbudget.antenna.Antenna gs_antenna: ground station antenna
        :~linkbudget.antenna.Antenna gs_antenna_pointing_loss: ground station antenna's pointing loss
        :~linkbudgets.receiver.DownlinkReceiver gs_receiver: ground station downlink receiver
        :~linkbudgets.transmitter.UplinkTransmitter gs_trasmitter: ground station uplink transmitter
        :~astropy.units.Unit gs_altitude: ground station altitude
        """
        self.gs_antenna = gs_antenna
        self.gs_antenna_pointing_loss = gs_antenna_pointing_loss
        self.gs_receiver = gs_receiver
        self.gs_transmitter = gs_transmitter
        self.gs_altitude = gs_altitude.to(u.m)

    @property
    def figure_of_merit(self):
        return self.gs_antenna.antenna_gain - self.gs_receiver.total_in_line_losses - self.gs_receiver.system_noise_temperature.to(
            u.dB(u.K))

    # TODO: Handle pointing losses in a more intuitive way
    @property
    def pointing_loss(self):
        return self.gs_antenna_pointing_loss

    @property
    def ground_station_eirp(self):
        return self.gs_transmitter.power_output - self.gs_transmitter.total_line_losses + 2.873 * u.dB
