import pandas as pd
from sqlalchemy import create_engine
URI = 'postgresql+psycopg2://postgres:postgres@database-1.c45apqxvtyvo.us-west-2.rds.amazonaws.com/postgres'
con = create_engine(URI)

data = pd.read_sql_table('models_score', con)
data.drop(data.index, inplace=True)
data.to_sql('models_score', if_exists='replace', index=False, con=con)