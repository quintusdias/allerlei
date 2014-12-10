import pandas as pd
import psycopg2
import sqlalchemy

connect_string = 'postgresql+psycopg2://jevans:99luftbaloons@localhost:5432/kepler'
engine = sqlalchemy.create_engine(connect_string)

conn = psycopg2.connect(database='kepler')
cursor = conn.cursor()
df = pd.io.sql.read_sql('select * from star', engine)
columns = df.columns[1:]
stars_df = pd.read_csv('stars.dat', header=None, index_col=None)
stars_df.columns = columns
stars_df.to_sql('star', engine, if_exists='append', index=False)
