"""
Create database tables for PHL HEC catalog.
"""
import re
import sys

import numpy as np
import pandas as pd
import psycopg2

planet_short_names = {
    'P. Name':              'name',
    'P. Name Kepler':       'name_kepler',
    'P. Name KOI':          'name_koi',
    'P. Zone Class':        'zone_class',
    'P. Mass Class':        'mass_class',
    'P. Composition Class': 'composition_class',
    'P. Atmosphere Class':  'atmosphere_class',
    'P. Habitable Class':   'habitable_class',
    'P. Min Mass (EU)':     'min_mass',
    'P. Mass (EU)':         'mass',
    'P. Max Mass (EU)':     'max_mass',
    'P. Radius (EU)':       'radius',
    'P. Density (EU)':      'density',
    'P. Gravity (EU)':      'gravity',
    'P. Esc Vel (EU)':      'esc_vel',
    'P. SFlux Min (EU)':    'sflux_min',
    'P. SFlux Mean (EU)':   'sflux_mean',
    'P. SFlux Max (EU)':    'sflux_max',
    'P. Teq Min (K)':       'teq_min',
    'P. Teq Mean (K)':      'teq_mean',
    'P. Teq Max (K)':       'teq_max',
    'P. Ts Min (K)':        'ts_min',
    'P. Ts Mean (K)':       'ts_mean',
    'P. Ts Max (K)':        'ts_max',
    'P. Surf Press (EU)':   'surf_press',
    'P. Mag':               'mag',
    'P. Appar Size (deg)':  'appar_size',
    'P. Period (days)':     'period',
    'P. Sem Major Axis (AU)':    'sem_major_axis',
    'P. Eccentricity':      'eccentricity',
    'P. Mean Distance (AU)':'mean_distance',
    'P. Inclination (deg)': 'inclination',
    'P. Omega (deg)':       'omega',
    'S. Name':              'star_name',
    'P. HZD':               'hzd',
    'P. HZC':               'hzc',
    'P. HZA':               'hza',
    'P. HZI':               'hzi',
    'P. SPH':               'sph',
    'P. Int ESI':           'int_esi',
    'P. Surf ESI':          'surf_esi',
    'P. ESI':               'esi',
    'P. Habitable':         'habitable',
    'P. Hab Moon':          'hab_moon',
    'P. Confirmed':         'confirmed',
    'P. Disc. Method':      'disc_method',
    'P. Disc. Year':        'disc_year',
        }

star_short_names = {'S. Name': 'name',
    'S. Name HD': 'name_hd',
    'S. Name HIP': 'name_hip',
    'S. Constellation': 'constellation',
    'S. Type': 'type',
    'S. Mass (SU)': 'mass',
    'S. Radius (SU)': 'radius',
    'S. Teff (K)': 'teff',
    'S. Luminosity (SU)': 'luminosity',
    'S. [Fe/H]': 'iron_hydrogen_ratio',
    'S. Age (Gyrs)': 'age',
    'S. Appar Mag': 'appar_mag',
    'S. Distance (pc)': 'distance',
    'S. RA (hrs)': 'ra',
    'S. DEC (deg)': 'dec',
    'S. Mag from Planet': 'mag_from_planet',
    'S. Size from Planet (deg)': 'size_from_planet',
    'S. No. Planets': 'num_planets',
    'S. No. Planets HZ': 'num_planets_hz',
    'S. Hab Zone Min (AU)': 'hab_zone_min',
    'S. Hab Zone Max (AU)': 'hab_zone_max',
    'S. HabCat': 'habcat'}

star_col_types = {'S. Name': 'varchar(50)',
    'S. Name HD': 'varchar(50)',
    'S. Name HIP': 'varchar(50)',
    'S. Constellation': 'varchar(50)',
    'S. Type': 'char(10)',
    'S. Mass (SU)': 'real',
    'S. Radius (SU)': 'real',
    'S. Teff (K)': 'real',
    'S. Luminosity (SU)': 'real',
    'S. [Fe/H]': 'real',
    'S. Age (Gyrs)': 'real',
    'S. Appar Mag': 'real',
    'S. Distance (pc)': 'real',
    'S. RA (hrs)': 'real',
    'S. DEC (deg)': 'real',
    'S. Mag from Planet': 'real',
    'S. Size from Planet (deg)': 'real',
    'S. No. Planets': 'int',
    'S. No. Planets HZ': 'int',
    'S. Hab Zone Min (AU)': 'real',
    'S. Hab Zone Max (AU)': 'real',
    'S. HabCat': 'int'}

numeric_long_names = [name for name, value in star_col_types.items() if value in ['real', 'int']]

def blank_converter(x):
    if re.match('\s*', x):
        return np.nan
    else:
        return x

def populate_planet_db(csv_file):
    """
    Populate planet table.
    """
    df = pd.read_csv(csv_file, converters={'P. SFlux Mean (EU)': blank_converter,
                                           'P. SFlux Min (EU)': blank_converter,
                                           'P. SFlux Max (EU)': blank_converter})

    conn = psycopg2.connect("dbname=phl user=jevans")
    cursor = conn.cursor()

    for _, row in df.iterrows():

        process_row(cursor, "planet", row, planet_short_names)

    conn.commit()
    cursor.close()
    conn.close()


def populate_star_db(csv_file):
    """
    Populate star table.
    """
    df = pd.read_csv(csv_file)

    conn = psycopg2.connect("dbname=phl user=jevans")
    cursor = conn.cursor()

    duplicates = []
    for _, row in df.iterrows():

        if row['S. Name'] in duplicates:
            # We've already seen this one, don't bother.
            # Otherwise we get a psycopg2.IntegrityError (23505) error and have
            # to roll back the entire set of inserts.
            continue

        process_row(cursor, "star", row, star_short_names)

        duplicates.append(row['S. Name'])

    conn.commit()
    cursor.close()
    conn.close()

def process_row(cursor, table_name, data_row, short_names):
    """
    """
    sql = "INSERT into {0} ({1}) VALUES ({2})"

    field_specifiers = ""
    name_fields = ""
    values = {}
    for long_name, short_name in short_names.items():
        field_specifiers += "%({0})s, ".format(short_name)
        name_fields += "{0}, ".format(short_name)

        if data_row[long_name] is np.nan:
            values[short_name] = None
        else:
            if short_name == 'disc_year':
                values['disc_year'] = str(int(data_row[long_name]))
            else:
                values[short_name] = data_row[long_name]


    name_fields = name_fields.rstrip(', ')
    field_specifiers = field_specifiers.rstrip(', ')

    sql = sql.format(table_name, name_fields, field_specifiers)

    try:
        cursor.execute(sql, values)
    except psycopg2.InternalError as err:
        if err.pgcode == '25P02':
            print(err)
            print(sql)
            print(values)
        raise



def create_planet_table():
    """
    Create the planet table.
    """
    conn = psycopg2.connect("dbname=phl user=jevans")
    cursor = conn.cursor()
    cursor.execute("DROP TYPE IF EXISTS zone_class_enum")
    cursor.execute("DROP TYPE IF EXISTS mass_class_enum")
    cursor.execute("DROP TYPE IF EXISTS composition_class_enum")
    cursor.execute("DROP TYPE IF EXISTS atmosphere_class_enum")
    cursor.execute("DROP TYPE IF EXISTS habitable_class_enum")
    cursor.execute("DROP TYPE IF EXISTS discovery_method_enum")
    cursor.execute("CREATE TYPE zone_class_enum AS ENUM('Hot','Warm','Cold')")
    cursor.execute("""CREATE TYPE mass_class_enum
                      AS ENUM('Mercurian','Subterran','Terran','Superterran',
                              'Neptunian','Jovian')""")
    cursor.execute("""CREATE TYPE composition_class_enum
                      AS ENUM('iron','rocky-iron','rocky-water','water-gas',
                              'gas')""")
    cursor.execute("""CREATE TYPE atmosphere_class_enum
                      AS ENUM('no-atmosphere','metals-rich','hydrogen-rich')""")
    cursor.execute("""CREATE TYPE habitable_class_enum
                      AS ENUM('mesoplanet','thermoplanet','psychroplanet',
                              'hypopsychroplanet','hyperthermoplanet',
                              'non-habitable')""")
    cursor.execute("""CREATE TYPE discovery_method_enum
                      AS ENUM('radial velocity','transit','TTV','imaging',
                              'microlensing','pulsar timing','astrometry')""")
    cursor.execute("DROP TABLE IF EXISTS planet")
    sql = r"""CREATE TABLE planet
              (name                varchar(50) PRIMARY KEY,
               name_kepler         varchar(50),
               name_koi            varchar(50),
               zone_class          zone_class_enum,
               mass_class          mass_class_enum,
               composition_class   composition_class_enum,
               atmosphere_class    atmosphere_class_enum,
               habitable_class     habitable_class_enum,
               min_mass            real,
               mass                real,
               max_mass            real,
               radius              real,
               density             real,
               gravity             real,
               esc_vel             real,
               sflux_min           real,
               sflux_mean          real,
               sflux_max           real,
               teq_min             real,
               teq_mean            real,
               teq_max             real,
               ts_min              real,
               ts_mean             real,
               ts_max              real,
               surf_press          real,
               mag                 real,
               appar_size          real,
               period              real,
               sem_major_axis      real,
               eccentricity        real,
               mean_distance       real,
               inclination         real,
               omega               real,
               star_name           varchar(50) references star(name),
               hzd                 real,
               hzc                 real,
               hza                 real,
               hzi                 real,
               sph                 real,
               int_esi             real,
               surf_esi            real,
               esi                 real,
               habcat              int,
               habitable           int,
               hab_moon            int,
               confirmed           int,
               disc_method         discovery_method_enum,
               disc_year           char(4))"""
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


def create_star_table():
    """
    Create the star table.
    """
    #df = pd.read_csv(csv_file)

    # collect the star columns.
    #starcols = [col for col in df.columns if col.startswith('S.')]

    # Create the database short name (no capitals, spaces, leading 'S. '
    #short_names = [col.lower().replace(' ', '_')[3:] for col in starcols]

    conn = psycopg2.connect("dbname=phl user=jevans")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS planet")
    cursor.execute("DROP TABLE IF EXISTS star")
    sql = r"""CREATE TABLE star
              (name                varchar(50) PRIMARY KEY,
               name_hd             varchar(50),
               name_hip            varchar(50),
               constellation       varchar(50),
               type                char(20),
               mass                real,
               radius              real,
               teff                real,
               luminosity          real,
               iron_hydrogen_ratio real,
               age                 real,
               appar_mag           real,
               distance            real,
               ra                  real,
               dec                 real,
               mag_from_planet     real,
               size_from_planet    real,
               num_planets         int,
               num_planets_hz      int,
               hab_zone_min        real,
               hab_zone_max        real,
               habcat              int)"""
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


def run(csv_file):
    """
    Create and populate the star and planet tables.
    """
    create_star_table()
    populate_star_db(csv_file)
    create_planet_table()
    populate_planet_db(csv_file)

if __name__ == '__main__':
    run(sys.argv[1])
