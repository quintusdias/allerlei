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
    df = pd.read_csv(csv_file)

    # collect the star columns.
    starcols = [col for col in df.columns if col.startswith('S.')]

    conn = psycopg2.connect("dbname=phl user=jevans")
    cursor = conn.cursor()

    for idx, s in df.iterrows():
        sql = "INSERT into star {0} VALUES {1}"

        name_fields = "("
        values_fields = "("
        values = []

        for long_name, short_name in star_short_names.items():
            name_fields += "{0}, ".format(short_name)
            values_fields += "%s, "

            if s[long_name] is np.nan:
                values.append(None)
            else:
                values.append(s[long_name])

        name_fields = name_fields.rstrip(', ') + ")"
        values_fields = values_fields.rstrip(', ') + ")"

        sql = sql.format(name_fields, values_fields)
        print(sql)
        print(values)
        try:
            cursor.execute(sql, tuple(values))
        except psycopg2.IntegrityError as err:
            if err.pgcode != '23505':
                # not a duplicate, something else is wrong
                raise
            print('encountered a duplicate')
            conn.rollback()
        except psycopg2.InternalError as err:
            import pdb; pdb.set_trace()
            if err.pgcode == '25P02':
                print(err)
                print(sql)
                print(values)

    conn.commit()
    cursor.close()
    conn.close()
              

def create_star_db(csv_file):
    df = pd.read_csv(csv_file)

    # collect the star columns.
    starcols = [col for col in df.columns if col.startswith('S.')]
    print(starcols)

    # Create the database short name (no capitals, spaces, leading 'S. '
    short_names = [col.lower().replace(' ', '_')[3:] for col in starcols]
    print(short_names)

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
    create_star_db(sys.argv[1])
    populate_star_db(sys.argv[1])

if __name__ == '__main__':
    run(sys.argv[1])
