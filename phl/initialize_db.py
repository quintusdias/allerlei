"""
Create database tables for PHL HEC catalog.
"""
import sys

import numpy as np
import pandas as pd
import psycopg2

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

        sql = "INSERT into star {0} VALUES {1}"

        name_fields = "("
        values_fields = "("
        values = []

        for long_name, short_name in star_short_names.items():
            name_fields += "{0}, ".format(short_name)
            values_fields += "%s, "

            if row[long_name] is np.nan:
                values.append(None)
            else:
                values.append(row[long_name])

        name_fields = name_fields.rstrip(', ') + ")"
        values_fields = values_fields.rstrip(', ') + ")"

        sql = sql.format(name_fields, values_fields)
        try:
            cursor.execute(sql, tuple(values))
        except psycopg2.InternalError as err:
            if err.pgcode == '25P02':
                print(err)
                print(sql)
                print(values)


        duplicates.append(row['S. Name'])

    conn.commit()
    cursor.close()
    conn.close()


def create_star_db():
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
    create_star_db()
    populate_star_db(csv_file)

if __name__ == '__main__':
    run(sys.argv[1])
