# Link Budget Calculator

Link budget calculator based on the [IARU calculator](www.amsatuk.me.uk/iaru/spreadsheet.htm) by Jan King

This is currently a - fairly undocumented - WIP. For example 
usage check out the tests.

## Installation

``git clone https://gitlab.com/acubesat/comms/link-budget.git``

``cd link-budget``

``python setup.py install``

## Example Usage

```python
# Ground Station
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
```



