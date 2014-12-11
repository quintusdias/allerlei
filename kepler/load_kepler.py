import pandas as pd
import psycopg2
import sqlalchemy

connect_string = 'postgresql+psycopg2://jevans:99luftbaloons@localhost:5432/kepler'
engine = sqlalchemy.create_engine(connect_string)

conn = psycopg2.connect(database='kepler')
cursor = conn.cursor()

#df = pd.io.sql.read_sql('select * from star', engine)
#columns = df.columns[1:]
#stars_df = pd.read_csv('stars.dat', header=None, index_col=None)
#stars_df.columns = columns
#stars_df.to_sql('star', engine, if_exists='append', index=False)

df = pd.io.sql.read_sql('select * from planet', engine)
columns = df.columns
#columns = 

def to_float_fun(x):
    try:
        return(float(x))
    except ValueError:
        return None

converters = {
        # Force to string
        'P. Name KOI':  str,
        # should be float
        'P. SFlux Min (EU)': to_float_fun,
        'P. SFlux Mean (EU)': to_float_fun,
        'P. SFlux Max (EU)': to_float_fun
    }


planets_df = pd.read_csv('/opt/data/csv/phl_hec_all_kepler.csv',
        index_col=None,
        converters=converters)

# Replace nan with None
planets_df = planets_df.where((pd.notnull(planets_df)), None)

print(planets_df.columns)
star = planets_df['S. Name']

# Drop everything from the planet table so we can safely reload it.
cursor.execute("TRUNCATE planet")

lst = []
for j, row in planets_df.iterrows():
   
    print(j)

    # Get the star ID
    sql = "select id from star where name=%(name)s"
    data = {'name': star[j]}
    cursor.execute(sql, data)
    results = cursor.fetchone()
    star_id = results[0]

    # Insert the planet data.
    sql = """
        INSERT INTO planet
            (
                name, star_id, name_kepler,
                name_koi, zone_class, mass_class, composition_class,
                atmosphere_class, habitable_class,
                min_mass, mass, max_mass,
                radius, density, gravity, escape_velocity,
                minimum_stellar_flux, mean_stellar_flux, maximum_stellar_flux,
                teq_min, teq_mean, teq_max
            )
        VALUES 
            (
                %(name)s, %(star_id)s, %(name_kepler)s,
                %(name_koi)s,
                %(zone_class)s, %(mass_class)s,
                %(composition_class)s, %(atmosphere_class)s, %(habitable_class)s,
                %(min_mass)s, %(mass)s, %(max_mass)s,
                %(radius)s, %(density)s, %(gravity)s, %(escape_velocity)s,
                %(minimum_stellar_flux)s, %(mean_stellar_flux)s,
                %(maximum_stellar_flux)s,
                %(teq_min)s, %(teq_mean)s, %(teq_max)s
            )
        """
    values = {
            'name': row['P. Name'],
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
            'teq_max': row['P. Teq Max (K)']
            }
    #print(values)
    cursor.execute(sql, values)


conn.commit()
conn.close()

