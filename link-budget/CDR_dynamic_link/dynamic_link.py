import scipy.io
import numpy as np
# from Cython.Includes.numpy import ndarray
from astropy import units as u
from astropy.tests.helper import assert_quantity_allclose
import matplotlib.pyplot as plt
from pycraf import conversions as cnv
from linkbudget.antenna import AntennaMeasured, Antenna
from linkbudget.ground_station import GroundStation
from linkbudget.receiver import DownlinkReceiver
from linkbudget.transmitter import DownlinkTransmitter
from linkbudget.spacecraft import Spacecraft
from linkbudget.link import Downlink
from linkbudget.utils import elevation_angle
from astropy.coordinates import EarthLocation
import math
import scipy.stats

# Advice to start the simulation after the first eclipse
start = 45000
sat_alt = []
sat_long = []
sat_lat = []
gs_lat = 40.627233
gs_long = 22.959887
gs_alt = 56 * u.m
r_earth = 6378.136

gs_coo = EarthLocation.from_geodetic(gs_long, gs_lat, gs_alt)
coordinates_LTAN_11 = './simulation_files/F10D-CL-COORDINATES-6.txt'
eclipse = scipy.io.loadmat('./simulation_files/eclipse11_6orb.mat')
performance_error = scipy.io.loadmat('simulation_files/APE0_3.mat')
ADCS_error_11 = np.array(performance_error['APE0_3'])
where_are_NaNs = np.isnan(ADCS_error_11)
ADCS_error_11[where_are_NaNs] = 0
ADCS_eclipse_11 = np.array(eclipse['eclipse'])
where_are_NaNs = np.isnan(ADCS_error_11)
ADCS_error_11[where_are_NaNs] = 0

# Procedure to take only the non-eclipse timestamps from ADCS pointing

j = 1
A = ADCS_error_11[:, 0].size
for time in ADCS_error_11:
    if ADCS_eclipse_11[0, j - 1] == 1 and j < A - 15000 and ADCS_eclipse_11[0, j] == 0:
        ADCS_eclipse_11[0, j:j + 15000] = 3
    j += 1
eclipse = np.where(ADCS_eclipse_11[0, :] != 0)
no_eclipse = np.where(ADCS_eclipse_11[0, :] == 0)
ADCS_error_no_eclipse = ADCS_error_11[no_eclipse, :]
ADCS_error_no_eclipse_11 = ADCS_error_no_eclipse[0, start:, :]

# Read the coordinates from GMAT file

with open(coordinates_LTAN_11, 'r') as f:
    for line in f:
        if line.startswith("#") or line.startswith(" ") or line.startswith("\n"):
            continue
        else:
            lines = line.strip("\n").split("   ")
            try:
                alt = lines[1]
                if lines[4] == "":
                    lat = lines[5]
                else:
                    lat = lines[4]
                if lines[7].strip("  ") == "":
                    long = lines[8]
                else:
                    long = lines[7]
                sat_alt.append(float(alt))
                sat_lat.append(float(lat))
                sat_long.append(float(long))
            except:
                print(line)
R = math.floor(len(ADCS_error_no_eclipse_11) / len(sat_long))
sat_alt = np.ndarray.flatten(np.array([sat_alt] * R))
sat_lat = np.ndarray.flatten(np.array([sat_lat] * R))
sat_long = np.ndarray.flatten(np.array([sat_long] * R))
sat_alt = sat_alt + 70
gain = np.genfromtxt('./simulation_files/farfield.txt')

# Gain of the antenna
D = np.genfromtxt('./Dipole_Measured_Directivity.txt')
e = 0.7
directivity = np.reshape(D, (181, 181))
gain = 0.7 * directivity
shape_ext = (2 * directivity.shape[0] - 1, 2 * directivity.shape[1] - 1)
rad_pat = np.empty(shape_ext)
theta_start = -180
theta_end = 180
theta_points = theta_end - theta_start + 1
phi_start = -180
phi_end = 180
phi_points = phi_end - phi_start + 1


for i, theta in enumerate(np.linspace(theta_start, theta_end, theta_points)):
    for j, phi in enumerate(np.linspace(phi_start, phi_end, phi_points)):
         if 0 <= theta <= 90 and -90 <= phi <= 90:
            rad_pat[i][j] = gain[i - 90][j - 90]
         else:
              rad_pat[i][j] = -7


G = np.max(rad_pat)
sc_antenna = AntennaMeasured(rad_pat, 1, np.linspace(theta_start, theta_end, theta_points),
                             np.linspace(phi_start, phi_end, phi_points))

# Static parts of the link budget

gs_antenna = Antenna(26.5 * cnv.dB)
dtransmitter = DownlinkTransmitter(1.6 * u.W, 0 * cnv.dB, 4, 0 * cnv.dB, 0.5 * cnv.dB, 0.23 * cnv.dB)
dreceiver = DownlinkReceiver((0.23 + 0.0276 + 0.0276) * cnv.dB, 1.7 * cnv.dB, 0 * cnv.dB, 4, 8 * u.K,
                              290 * u.K, 45.3 * u.K,
                             44 * cnv.dB, 0.1 * cnv.dB, 1000 * u.K)
ground_station = GroundStation(gs_antenna, 0 * cnv.dB, dreceiver, dtransmitter, 56 * u.m)
spacecraft = Spacecraft(sc_antenna, 0 * cnv.dB, dtransmitter, dtransmitter, 500 * u.km)
dlink = Downlink(ground_station, spacecraft, 2.4 * u.GHz, 20 * u.deg, 0.5 * cnv.dB,
                  220000, 1e-6, 1 * cnv.dB, 6.1 * cnv.dB)



theta_ADCS = ADCS_error_no_eclipse_11[0:, 2]
phi_ADCS = ADCS_error_no_eclipse_11[0:, 1]
dlink.elev_angle = []
elev_angle = []

for i in range(len(sat_long)):
    sat_coo = EarthLocation.from_geodetic(sat_long[i], sat_lat[i], (sat_alt[i] * 1000))
    dlink.elev_angle = elevation_angle(sat_coo, gs_coo)
    elev_angle.append(dlink.elev_angle.value)

r_earth_v = np.array([r_earth] * len(elev_angle))
ratio = np.divide(r_earth_v, (r_earth_v + sat_alt[0:len(elev_angle)]))
elev_angle = [elev_angle[i] * math.pi / 180 for i in range(len(elev_angle))]
arg = np.multiply(ratio, np.cos(elev_angle))
theta_sc = np.arcsin(arg) * 180 / math.pi + np.array(theta_ADCS[0:len(arg)])

i = 0
link = []
loss = []
g = []
indeces = [i for i in range(len(arg))]
arg = np.delete(arg, indeces)
ratio = np.delete(ratio, indeces)
r_earth_v = np.delete(r_earth_v, indeces)
elev_angle = np.delete(elev_angle, indeces)
ADCS_error_no_eclipse = np.delete(ADCS_error_no_eclipse, indeces)
theta_ADCS = np.delete(theta_ADCS, indeces)

for errors in sat_lat:
    try:
        sat_coo = EarthLocation.from_geodetic(sat_long[i], sat_lat[i], (sat_alt[i] * 1000))
    except:
        print("Sat coo")

    spacecraft.sc_altitude = sat_alt[i] * u.km
    dlink.elev_angle = elevation_angle(sat_coo, gs_coo)
    g.append(sc_antenna.gain_p(theta_sc[i], phi_ADCS[i]))
    loss.append((G - sc_antenna.gain_p(theta_sc[i], phi_ADCS[i])))
    spacecraft.pointing_loss = loss[i] * cnv.dB
    link.append(dlink.link_margin.value)
    i += 1


x = [i * 0.1 for i in range(len(link))]
plt.plot(x, link)
plt.xlabel('Time (s)')
plt.ylabel('Link Margin (dB)')
plt.title('Dynamic Link Budget')
plt.grid(color='g', linestyle='--', linewidth=0.5)
plt.show()

plt.plot(x, loss)
plt.xlabel('Time (s)')
plt.ylabel('Pointing Loss (dB)')
plt.title('Dynamic Link Budget')
plt.grid(color='g', linestyle='--', linewidth=0.5)
plt.show()
