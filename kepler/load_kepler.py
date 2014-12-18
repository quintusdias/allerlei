import pandas as pd
import psycopg2


def to_bool(x):
    """
    convert to boolean in the database
    """
    return bool(int(x))


def to_float_func(x):
    """
    Convert a string to float.  If the string is '-', that should become NULL
    in the database.
    """
    try:
        return(float(x))
    except (ValueError, psycopg2.DataError):
        return None


class KeplerPG(object):
    """
    Loads PHL exoplanet data into PostgreSQL database.
    """
    star_insert_sql = """
        INSERT INTO stars (
            name, name_hd, name_hip,
            constellation,
            type, mass, radius, teff, luminosity, fe_h,
            age, appar_mag, distance, right_ascension, declination,
            num_planets, num_planets_hab_zone,
            hab_zone_min, hab_zone_max,
            hab_cat
        ) VALUES (
            %(name)s, %(name_hd)s, %(name_hip)s, %(constellation)s,
            %(type)s, %(mass)s, %(radius)s, %(teff)s, %(luminosity)s, %(fe_h)s,
            %(age)s, %(appar_mag)s, %(distance)s, %(right_ascension)s,
            %(declination)s, %(num_planets)s, %(num_planets_hab_zone)s,
            %(hab_zone_min)s, %(hab_zone_max)s, %(hab_cat)s
        )
    """

    planet_insert_sql = """
        INSERT INTO planets (
            name, star_id, name_kepler, name_koi,
            zone_class, mass_class, composition_class,
            atmosphere_class, habitable_class, min_mass,
            mass, max_mass, radius, density, gravity,
            escape_velocity, minimum_stellar_flux,
            mean_stellar_flux, maximum_stellar_flux,
            teq_min, teq_mean, teq_max,
            ts_min, ts_mean, ts_max,
            surf_pres, magnitude, appar_size,
            period, semi_major_axis, eccentricity,
            mean_distance, inclination, omega,
            star_magnitude_from_planet, star_size_from_planet,
            hzd, hzc, hza, hzi,
            sph, int_esi, surf_esi, esi,
            habitable, hab_moon, confirmed,
            discovery_method, discovery_year
        ) VALUES (
            %(name)s, %(star_id)s, %(name_kepler)s, %(name_koi)s,
            %(zone_class)s, %(mass_class)s, %(composition_class)s,
            %(atmosphere_class)s, %(habitable_class)s, %(min_mass)s,
            %(mass)s, %(max_mass)s, %(radius)s, %(density)s, %(gravity)s,
            %(escape_velocity)s, %(minimum_stellar_flux)s,
            %(mean_stellar_flux)s, %(maximum_stellar_flux)s,
            %(teq_min)s, %(teq_mean)s, %(teq_max)s,
            %(ts_min)s, %(ts_mean)s, %(ts_max)s,
            %(surf_pres)s, %(magnitude)s, %(appar_size)s,
            %(period)s, %(semi_major_axis)s, %(eccentricity)s,
            %(mean_distance)s, %(inclination)s, %(omega)s,
            %(star_magnitude_from_planet)s, %(star_size_from_planet)s,
            %(hzd)s, %(hzc)s, %(hza)s, %(hzi)s,
            %(sph)s, %(int_esi)s, %(surf_esi)s, %(esi)s,
            %(habitable)s, %(hab_moon)s, %(confirmed)s,
            %(discovery_method)s, %(discovery_year)s
        )
    """

    def __init__(self):
        """
        establish database connections
        """
        self.conn = psycopg2.connect(database='kepler')
        self.cursor = self.conn.cursor()

    def load_stars(self):
        """
        load star data
        """
        print('truncating star...')
        self.cursor.execute("TRUNCATE stars CASCADE")
        print('done truncating star...')

        converters = {'S. HabCat': lambda x: bool(int(x))}

        print('inserting star data ...')
        df = pd.read_csv('/opt/data/csv/phl_hec_all_confirmed.csv',
                         index_col=None,
                         converters=converters)

        # Replace nan with None
        df = df.where((pd.notnull(df)), None)
        print("{0} rows before dropping duplicates...".format(df.shape[0]))

        # Reduce down to unique stars.
        df = df.drop_duplicates(subset='S. Name')
        print("{0} rows after dropping duplicates...".format(df.shape[0]))

        for j, row in df.iterrows():
            # print(j)

            values = {'name': row['S. Name'],
                      'name_hd': row['S. Name HD'],
                      'name_hip': row['S. Name HIP'],
                      'constellation': row['S. Constellation'],
                      'type': row['S. Type'],
                      'mass': row['S. Mass (SU)'],
                      'radius': row['S. Radius (SU)'],
                      'teff': row['S. Teff (K)'],
                      'luminosity': row['S. Luminosity (SU)'],
                      'fe_h': row['S. [Fe/H]'],
                      'age': row['S. Age (Gyrs)'],
                      'appar_mag': row['S. Appar Mag'],
                      'distance': row['S. Distance (pc)'],
                      'right_ascension': row['S. RA (hrs)'],
                      'declination': row['S. DEC (deg)'],
                      'num_planets': row['S. No. Planets'],
                      'num_planets_hab_zone': row['S. No. Planets HZ'],
                      'hab_zone_min': row['S. Hab Zone Min (AU)'],
                      'hab_zone_max': row['S. Hab Zone Max (AU)'],
                      'hab_cat': row['S. HabCat']}

            # print(values)
            self.cursor.execute(self.star_insert_sql, values)

        self.conn.commit()
        print('done inserting star data ...')

    def load_planets(self):
        """
        """
        # Drop everything from the planet table so we can safely reload it.
        print('truncating...')
        self.cursor.execute("TRUNCATE planets")
        print('done truncating')

        # Certain columns need data transformations.
        converters = {'P. Name KOI':  str,
                      'P. SFlux Min (EU)': to_float_func,
                      'P. SFlux Mean (EU)': to_float_func,
                      'P. SFlux Max (EU)': to_float_func,
                      'P. Appar Size (deg)':  to_float_func,
                      'S. Size from Planet (deg)':  to_float_func,
                      'S. HabCat': bool,
                      'P. Habitable': to_bool,
                      'P. Hab Moon': bool,
                      'P. Confirmed': bool}

        planets_df = pd.read_csv('/opt/data/csv/phl_hec_all_confirmed.csv',
                                 index_col=None,
                                 converters=converters)

        # Replace nan with None
        planets_df = planets_df.where((pd.notnull(planets_df)), None)

        star = planets_df['S. Name']

        for j, row in planets_df.iterrows():
            # print(j)

            # Get the star ID
            sql = "select id from stars where name=%(name)s"
            data = {'name': star[j]}
            self.cursor.execute(sql, data)
            results = self.cursor.fetchone()
            star_id = results[0]

            values = {'name': row['P. Name'],
                      'star_id': star_id,
                      'name_kepler': row['P. Name Kepler'],
                      'name_koi': row['P. Name KOI'],
                      'zone_class': row['P. Zone Class'],
                      'mass_class': row['P. Mass Class'],
                      'composition_class': row['P. Composition Class'],
                      'atmosphere_class': row['P. Atmosphere Class'],
                      'habitable_class': row['P. Habitable Class'],
                      'min_mass': row['P. Min Mass (EU)'],
                      'mass': row['P. Mass (EU)'],
                      'max_mass': row['P. Max Mass (EU)'],
                      'radius': row['P. Radius (EU)'],
                      'density': row['P. Density (EU)'],
                      'gravity': row['P. Gravity (EU)'],
                      'escape_velocity': row['P. Esc Vel (EU)'],
                      'minimum_stellar_flux': row['P. SFlux Min (EU)'],
                      'mean_stellar_flux': row['P. SFlux Mean (EU)'],
                      'maximum_stellar_flux': row['P. SFlux Max (EU)'],
                      'teq_min': row['P. Teq Min (K)'],
                      'teq_mean': row['P. Teq Mean (K)'],
                      'teq_max': row['P. Teq Max (K)'],
                      'ts_min': row['P. Ts Min (K)'],
                      'ts_mean': row['P. Ts Mean (K)'],
                      'ts_max': row['P. Ts Max (K)'],
                      'surf_pres': row['P. Surf Press (EU)'],
                      'magnitude': row['P. Mag'],
                      'appar_size': row['P. Appar Size (deg)'],
                      'period': row['P. Period (days)'],
                      'semi_major_axis': row['P. Sem Major Axis (AU)'],
                      'eccentricity': row['P. Eccentricity'],
                      'mean_distance': row['P. Mean Distance (AU)'],
                      'inclination': row['P. Inclination (deg)'],
                      'omega': row['P. Omega (deg)'],
                      'star_magnitude_from_planet': row['S. Mag from Planet'],
                      'star_size_from_planet': row['S. Size from Planet (deg)'],
                      'hzd': row['P. HZD'],
                      'hzc': row['P. HZC'],
                      'hza': row['P. HZA'],
                      'hzi': row['P. HZI'],
                      'sph':  row['P. SPH'],
                      'int_esi':  row['P. Int ESI'],
                      'surf_esi':  row['P. Surf ESI'],
                      'esi':  row['P. ESI'],
                      'habitable': row['P. Habitable'],
                      'hab_moon':  row['P. Hab Moon'],
                      'confirmed': row['P. Confirmed'],
                      'discovery_method': row['P. Disc. Method'],
                      'discovery_year': row['P. Disc. Year']}
            # print(values)
            self.cursor.execute(self.planet_insert_sql, values)

        self.conn.commit()


if __name__ == "__main__":

    ko = KeplerPG()
    ko.load_stars()
    ko.load_planets()
    ko.conn.commit()
    ko.conn.close()
