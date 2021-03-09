import numpy as np
from astropy import units as u
from pycraf import conversions as cnv
from scipy.integrate import simps
from scipy.interpolate import interp2d


class Antenna:
    def __init__(self, antenna_gain):
        self._antenna_gain = antenna_gain.to(cnv.dB)

    @property
    def antenna_gain(self):
        return self._antenna_gain


class AntennaMeasured(Antenna):
    def __init__(self, rad_pattern, antenna_e, rad_pattern_theta=None, rad_pattern_phi=None):
        """
        :~numpy.array rad_pattern: 2D array of antenna radiation intensity
         :float antenna_e: efficiency of antenna
        :~numpy.array rad_pattern_theta: theta angles corresponding to the antenna gain values. If not specified,
                                         we assume the values to be equidistant (in the range [-pi/2, pi/2])
        :~numpy.array rad_pattern_phi: phi angles corresponding to the antenna gain values. If not specified,
                                         we assume the values to be equidistant (in the range [-pi, pi])
        """
        self.rad_pattern = rad_pattern
        self.antenna_e = antenna_e

        # Dimensions of radiation intensity measures
        n, k = self.rad_pattern.shape

        # if the theta aren't specified, we take the partition of [-pi/2, pi/2]
        if not rad_pattern_theta.any():
            self.rad_pattern_theta = np.array(np.linspace(-np.pi / 2, np.pi / 2, n))
        else:
            self.rad_pattern_theta = rad_pattern_theta

        # if the phi angles aren't specified, we take the partition of [-pi, pi]
        if not rad_pattern_phi.any():
            self.rad_pattern_phi = np.array(np.linspace(-np.pi, np.pi, k))
        else:
            self.rad_pattern_phi = rad_pattern_phi

        # Interpolating spline
        self.rad_pattern_spline = interp2d(self.rad_pattern_phi, self.rad_pattern_theta, self.rad_pattern)

        # There is currently no real need to call the constructor of the parent class
        super().__init__(self.gain)

    @property
    def total_radiated_power(self):
        # Convert to polar coordinates
        rad_pat_pol = (self.rad_pattern.T * np.sin(self.rad_pattern_theta)).T
        # To find the total radiated power we calculate the double integral of the radiation intensity using
        # Simpson's rule
        total_rad_power = simps([simps(rad_pattern_th, self.rad_pattern_phi) for rad_pattern_th in rad_pat_pol],
                                self.rad_pattern_theta)
        return total_rad_power

    @property
    def mean_radiation_intensity(self):
        return self.total_radiated_power / (4 * np.pi)

    def directivity(self, theta, phi):
        return self.rad_pattern_spline(theta, phi)[0] / self.mean_radiation_intensity

    def gain_p(self, theta, phi):
        return self.rad_pattern_spline(theta, phi)[0]

    @property
    def gain(self):
        return (self.antenna_e * np.max(self.rad_pattern) / self.mean_radiation_intensity) * cnv.dB


# TODO: Currently only axial-mode is supported
class AntennaHelical(Antenna):

    def __init__(self, circumference, turns_n, turns_spacing, wavelength):
        """
        :~astropy.units.Unit curcumference: circumference of the helix
        :int turns_n: number of turns
        :~astropy.units.Unit turns_spacing: spacing between turns
        :~astropy.units.Unit wavelength: wavelength of radio waves
        """
        self.circumference = circumference
        self.turns_n = turns_n
        self.turns_spacing = turns_spacing
        self.wavelength = wavelength
        if not (
                3 / 4 <= self.circumference / self.wavelength <= 4 / 3 and 11.5 * u.deg <= self.pitch_angle <= 14.5 * u.deg):
            raise Warning("Currently only axial-mode is supported, results may not be entirely accurate")
        super().__init__(self.gain)

    @property
    def diameter(self):
        return self.circumference / np.pi

    @property
    def axial_length(self):
        return self.turns_n * self.turns_spacing

    @property
    def pitch_angle(self):
        return np.arctan(self.turns_spacing / self.circumference)

    @property
    def gain(self):
        return (15 * self.circumference ** 2 * self.axial_length / self.wavelength ** 3) * cnv.dB

    @property
    def half_power_beamwidth(self):
        return 52 / (np.sqrt(self.axial_length / self.wavelength) * self.circumference / self.wavelength)

# TODO? Noncircular reflectors
class AntennaParabolicReflector(Antenna):
    def __init__(self, diameter, wavelength, aperture_efficiency):
        """
        :~astropy.units.Unit diameter: diameter of the reflector
        :~astropy.units.Unit wavelength: wavelength of radio waves
        :~astropy.units.Unit aperture_efficiency: aperture efficiency of the anteenna
        """
        self.diameter = diameter
        self.wavelength = wavelength
        self.aperture_efficiency = aperture_efficiency
        super().__init__(self.gain)

    @property
    def gain(self):
        return (self.aperture_efficiency*(np.pi*self.diameter/self.wavelength)**2) * cnv.dB
