import numpy as np

from astropy import units as u


def slant_range(sc_altitude, gs_altitude, elev_angle):
    """
    Calculate the slant-range (assuming spherical Earth)
    #TODO? Also compute slant-range given geocentric angle
    :~astropy.units.Unit sc_altitude: Altitude of spacecraft
    :~astropy.units.Unit gs_altitude: Altitude of ground station
    :~astropy.units.Unit elev_angle: Elevation angle with respect to the horizon (>= 0)
    """
    r_earth = 6378.136 * u.km  # Earth's radius
    d = -(r_earth + gs_altitude) * np.sin(elev_angle) + np.sqrt(
        np.square(r_earth + gs_altitude) * np.square(np.sin(elev_angle)) +
        np.square(sc_altitude) - np.square(gs_altitude) +
        2 * r_earth * (sc_altitude - gs_altitude))
    return d


def elevation_angle(sat, gs):
    """ Find the elevation angle of the satellite with respect to the ground station given the geodetic coordinates
    of the satellite and ground station
    :~astropy.coordinates.EarthLocation sat: Location of satellite
    :~astropy.coordinates.EarthLocation gs: Location of ground station
    """
    # Turns out it's way easier to do this in Cartesian coordinates

    # Normalize units and convert to numpy array which makes vector operations easier
    sat_cart = np.array(
        [sat.x.to(u.m).value, sat.y.to(u.m).value, sat.z.to(u.m).value])  # Cartesian satellite coordinates
    gs_cart = np.array(
        [gs.x.to(u.m).value, gs.y.to(u.m).value, gs.z.to(u.m).value])  # Cartesian ground station coordinates

    d = sat_cart - gs_cart

    # Semi-major axes of the Earth ellipsoid (WGS-84)
    a, b, c = 6378137, 6378137, 6356752.3142451793
    # Outward-facing normal of the ellipsoid on the ground station
    gs_normal = np.array([gs_cart[0] / a ** 2, gs_cart[1] / b ** 2, gs_cart[2] / c ** 2])

    # Determine if the point of the satellite lies above the tangential plane
    is_visible = 1 if np.dot(gs_normal, d) > 0 else -1

    elevation = np.rad2deg(np.arccos(np.dot(gs_normal, d) / (np.linalg.norm(gs_normal) * np.linalg.norm(d)))) * u.deg

    return 90 * u.deg - elevation if is_visible else - elevation
