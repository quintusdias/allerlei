import pandas as pd
import psycopg2
import sqlalchemy

connect_string = 'postgresql+psycopg2://jevans@localhost/kepler'
engine = sqlalchemy.create_engine(connect_string)

conn = psycopg2.connect(database='kepler')
df = pd.io.sql.read_sql('select * from star', engine)
print(df)
