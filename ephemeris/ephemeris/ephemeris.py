import argparse

import numpy as np

def sun_angle_subtended_from_planet(planet, aphelion=True):
    """
    Returns
    -------
    Angle subtended in minutes
    """
    pconfig = config[planet]
    sconfig = config['Sun']

    d = sconfig['r'] * 2
    a = pconfig['a']
    e = pconfig['e']
    if aphelion:
        return d / (a * (1 - e))* 180 / np.pi * 60
    else:
        return d / (a * (1 + e))* 180 / np.pi * 60

def moon_angle_subtended_from_other_moon(planet, moon1, moon2):
    """
    The point of view is moon1.
    """
    pconfig = config[planet]
    m1config = pconfig['moons'][moon1]
    m2config = pconfig['moons'][moon2]

    d = m2config['r'] * 2
    m1a = m1config['a']
    m2a = m2config['a']
    m1e = m1config['e']
    m2e = m2config['e']

    if m1config['a'] < m2config['a']:
        # if moon1 is interior to moon2, the nearest measurement is when moon1
        # is at apolune and moon2 is at perilune at conjunction.
        a = m2a * (1 - m2e) - m1a * (1 + m1e)
        s1 = d / a * 180 / np.pi * 60

        # The smallest measurement is when both moons are at apolune at
        # opposition.
        a = m2a * (1 + m2e) + m1a * (1 + m1e)
        s2 = d / a * 180 / np.pi * 60
    else:
        # if moon1 is exterior to moon2, the nearest measurement is when moon1
        # is at perilune and moon2 is at apolune at conjunction.
        a = m1a * (1 - m1e) - m2a * (1 + m2e)
        s1 = d / a * 180 / np.pi * 60

        # The smallest measurement is when moon2 is a apolune at opposition.
        a = m2a * (1 + m2e) + m1a * (1 + m1e)
        s2 = d / a * 180 / np.pi * 60
    return s1, s2



def skies_of(planet=None, moon=None):
    """
    How big do the other moons look from the planet?
    """
    if moon is not None:
        skies_of_moon(planet=planet, moon=moon)
    else:
        skies_of_planet(planet)

def skies_of_planet(planet):
    moon_transit(planet)

def skies_of_moon(moon, planet):
    """
    How big do the other moons look from the planet?
    """
    sa = sun_angle_subtended_from_planet(planet, aphelion=True)
    sp = sun_angle_subtended_from_planet(planet, aphelion=False)
    print(f'Sun:  [{sp:.3f} - {sa:.3f}]')

    sa = planet_angle_subtended_from_moon(planet, moon, aphelion=True)
    sp = planet_angle_subtended_from_moon(planet, moon, aphelion=False)
    print(f'{planet}:  [{sp:.3f} - {sa:.3f}]')

    for other_moon in config[planet]['moons'].keys():
        if other_moon == moon:
            continue

        s1, s2 = moon_angle_subtended_from_other_moon(planet, moon, other_moon)
        print(f'{other_moon}:  [{s1:.1f} - {s2:.1f}]')

def moon_angle_subtended_from_planet(planet, moon, aphelion=True):
    """
    Returns
    -------
    Angle subtended in minutes
    """
    pconfig = config[planet]
    mconfig = pconfig['moons'][moon]

    d = mconfig['r'] * 2
    a = mconfig['a']
    e = mconfig['e']
    if aphelion:
        return d / (a * (1 - e) - pconfig['r']) * 180 / np.pi * 60
    else:
        return d / (a * (1 + e) - pconfig['r']) * 180 / np.pi * 60

def planet_angle_subtended_from_moon(planet, moon, aphelion=True):
    pconfig = config[planet]
    mconfig = pconfig['moons'][moon]

    d = pconfig['r'] * 2
    a = mconfig['a']
    e = mconfig['e']

    if aphelion:
        return d / (a * (1 - e) - mconfig['r']) * 180 / np.pi * 60
    else:
        return d / (a * (1 + e) - mconfig['r']) * 180 / np.pi * 60

    return pconfig['r'] * 2 / (mconfig['a'] - mconfig['r']) * 180 / np.pi 

def planet_transit(planet):
    sa = sun_angle_subtended_from_planet(planet, aphelion=True)
    sp = sun_angle_subtended_from_planet(planet, aphelion=False)
    print(f'Sun:  [{sp:.3f} - {sa:.3f}]')
    for moon in config[planet]['moons'].keys():
        s = planet_angle_subtended_from_moon(planet, moon)
        print(f'{moon}:  {s:.3f}')

def moon_transit(planet):
    sa = sun_angle_subtended_from_planet(planet, aphelion=True)
    sp = sun_angle_subtended_from_planet(planet, aphelion=False)
    print(f'Sun:  [{sp:.1f} - {sa:.1f}]')
    for moon in config[planet]['moons'].keys():
        sa = moon_angle_subtended_from_planet(planet, moon, aphelion=True)
        sp = moon_angle_subtended_from_planet(planet, moon, aphelion=False)
        print(f'{moon}:  [{sp:.1f} - {sa:.1f}]')

config = {
    'Sun': {
        'r': 695700,
    },
    'Earth': {
        'a': 149598023,
        'r': 6371,
        'e': 0.0167,
        'moons': {
            'Luna': {
                'r':  1737,
                'a': 384399,
                'e': 0.0549,
            },
        }
    },
    'Mars': {
        'a': 227939200,
        'r': 3396,
        'e': 0.0934,
        'moons': {
            'Phobos': {
                'r':  11,
                'a': 9377,
                'e': 0.0,
            },
            'Deimos': {
                'r':  6.3,
                'a': 23460,
                'e': 0.0,
            },
        }
    },
    'Jupiter': {
        'a': 778.57e6,
        'r': 69911,
        'e': 0.0484,
        'moons': {
            'Metis': {
                'r':  40,
                'a': 128852,
                'e': 0.0077,
            },
            'Adrastea': {
                'r':  17,
                'a': 129000,
                'e': 0.0063,
            },
            'Amalthea': {
                'r':  167,
                'a': 181366,
                'e': 0.0075,
            },
            'Thebe': {
                'r':  98,
                'a': 221889,
                'e': 0.0180,
            },
            'Io': {
                'r':  1818,
                'a': 421700,
                'e': 0.0041,
            },
            'Europa': {
                'r':  1560,
                'a': 671034,
                'e': 0.0094,
            },
            'Ganymede': {
                'r':  2631,
                'a': 1070412,
                'e': 0.0011,
            },
            'Callisto': {
                'r':  2410,
                'a': 1882709,
                'e': 0.0074,
            },
        }
    },
    'Saturn': {
        'a': 2143739669.59,
        'r': 58232,
        'e': 0.0565,
        'moons': {
            'Pan': {
                'r': 29,
                'a': 133584,
                'e': 0.0,
            },
            'Mimas': {
                'r': 198,
                'a': 185404,
                'e': 0.0202,
            },
            'Enceladus': {
                'r': 252,
                'a': 237950,
                'e': 0.00407,
            },
            'Tethys': {
                'r': 531,
                'a': 294619,
                'e': 0.0001,
            },
            'Dione': {
                'r': 561.5,
                'a': 377396,
                'e': 0.0022,
            },
            'Rhea': {
                'r': 763.5,
                'a': 527108,
                'e': 0.001258,
            },
            'Titan': {
                'r': 2574.5,
                'a': 1221930,
                'e': 0.0288,
            },
            'Hyperion': {
                'r': 135,
                'a': 1481010,
                'e': 0.123,
            },
            'Iapetus': {
                'r': 734,
                'a': 3560820,
                'e': 0.028613,
            },
            'Phoebe': {
                'r': 106.5,
                'a': 12869700,
                'e': 0.156242,
            },
        },
    },
    'Uranus': {
        'a': 2875034645.2232,
        'r': 25362,
        'e': 0.046381,
        'moons': {
            'Cordelia': {
                'r': 20,
                'a': 49770,
                'e': 0.00026,
            },
            'Portia': {
                'r': 135,
                'a': 66090,
                'e': 0.00005,
            },
            'Mab': {
                'r': 12,
                'a': 97700,
                'e': 0.0025,
            },
            'Miranda': {
                'r': 236,
                'a': 129390,
                'e': 0.0013,
            },
            'Ariel': {
                'r': 579,
                'a': 191020,
                'e': 0.0012,
            },
            'Umbriel': {
                'r': 585,
                'a': 266300,
                'e': 0.0039,
            },
            'Titania': {
                'r': 788,
                'a': 435910,
                'e': 0.0011,
            },
            'Oberon': {
                'r': 761,
                'a': 583520,
                'e': 0.0014,
            },
        },
    },
    'Neptune': {
        'a': 4.489586268253e9,
        'r': 24764,
        'e': 0.009456,
        'moons': {
            'Naiad': {
                'r': 33,
                'a': 48227,
                'e': 0.0003,
            },
            'Larissa': {
                'r': 87,
                'a': 73548,
                'e': 0.0014,
            },
            'Proteus': {
                'r': 210,
                'a': 117646,
                'e': 0.005,
            },
            'Triton': {
                'r': 1352,
                'a': 354759,
                'e': 0.0,
            },
            'Nereid': {
                'r': 170,
                'a': 5513818,
                'e': 0.7507,
            },
        },
    },
    'Pluto': {
        'a': 5.906e9,
        'r': 1188,
        'e': 0.2488,
        'moons': {
            'Charon': {
                'r': 604,
                'a': 17536,
                'e': 0.0022,
            },
            'Styx': {
                'r': 11,
                'a': 42656,
                'e': 0.0058,
            },
            'Nix': {
                'r': 49,
                'a': 48694,
                'e': 0.002036,
            },
            'Kerberos': {
                'r': 13,
                'a': 57783,
                'e': 0.00328,
            },
            'Hydra': {
                'r': 45,
                'a': 64738,
                'e': 0.005862,
            },
        }
    }
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('planet', choices=config.keys())
    parser.add_argument('moon')
    args = parser.parse_args()

    skies_of(planet=args.planet, moon=args.moon)
