from pycraf import conversions as cnv


class Transmitter:
    def __init__(self, power_output, guide_loss, connectors, filter_insertion_losses, other_in_line_losses,
                 mismatch_losses):
        self.power_output = power_output.to(cnv.dB_W)
        self.guide_loss = guide_loss.to(cnv.dB)
        self.connectors = connectors
        self.filter_insertion_losses = filter_insertion_losses.to(cnv.dB)
        self.other_in_line_losses = other_in_line_losses.to(cnv.dB)
        self.mismatch_losses = mismatch_losses.to(cnv.dB)

    @property
    def total_line_losses(self):
        """ Total line losses"""
        return 0.05 * self.connectors * cnv.dB + self.guide_loss + self.filter_insertion_losses + self.other_in_line_losses + \
               self.mismatch_losses

    @property
    def delivered_power(self):
        return (self.power_output - self.total_line_losses).to(cnv.dB_W)


class DownlinkTransmitter(Transmitter):
    def __init__(self, power_output, guide_loss, connectors, filter_insertion_losses, other_in_line_losses,
                 mismatch_losses):
        """
        :~astropy.units.Unit power output: transmitter output power
        :~astropy.units.Unit guide_loss: total cable guide loss
        :int connectors: number of in-line connectors
        :~astropy.units.Unit filter_insertion_losses: filter insertion losses
        :~astropy.units.Unit other_in_line_losses: in-line losses
        :~astropy.units.Unit mismatch_losses: spacecraft antenna mismatch losses
        """
        super().__init__(power_output, guide_loss, connectors, filter_insertion_losses, other_in_line_losses,
                         mismatch_losses)


class UplinkTransmitter(Transmitter):
    def __init__(self, power_output, guide_loss, connectors, filter_insertion_losses, other_in_line_losses,
                 mismatch_losses):
        """
        :~astropy.units.Unit power output: transmitter output power
        :~astropy.units.Unit guide_loss: total cable guide loss
        :int connectors: number of in-line connectors
        :~astropy.units.Unit filter_insertion_losses: filter insertion losses
        :~astropy.units.Unit other_in_line_losses: in-line losses
        :~astropy.units.Unit mismatch_losses: ground station antenna mismatch losses
        """
        super().__init__(power_output, guide_loss, connectors, filter_insertion_losses, other_in_line_losses,
                         mismatch_losses)
