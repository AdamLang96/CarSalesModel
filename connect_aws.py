from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, VARCHAR, Numeric
from sqlalchemy import Table, text
from sqlalchemy.ext.declarative import declarative_base
import sklearn
import pandas as pd
import re
import os
uri = "postgresql://codesmith:TensorFlow01?@cardata.ceq8tkxrvrbb.us-west-2.rds.amazonaws.com:5432/postgres"
engine = create_engine(uri)
# # Base = declarative_base()

# # # class CarsBidsData(Base):
# # #     __tablename__ = 'models_score'
# # #     id_ =               Column(Integer, primary_key=True)
# # #     path =              Column(VARCHAR)
# # #     score =             Column(Numeric)
    
# # # Base.metadata.create_all(engine)


with engine.connect() as conn:
    sqlstmt = '''SELECT * FROM models_score'''
    ret = conn.execute(sqlstmt).fetchall()

print(ret)

# data = pd.read_sql_table("CarsBidData", con=engine)
# print(data.columns)
# print(data.shape)

