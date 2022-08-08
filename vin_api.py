import numpy as np
import pandas as pd
import requests as rq
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, VARCHAR, Numeric
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
from bs4 import BeautifulSoup

def getVinInfo(API_KEY = 'VA_DEMO_KEY', VIN = 'WDBUF65J64A534963', NUM_DAYS = 90, MILEAGE = 'average'):
  # 'average' if none specified
  URL = f'https://marketvalue.vinaudit.com/getmarketvalue.php?key={API_KEY}&vin={VIN}&format=json&period={NUM_DAYS}&mileage={MILEAGE}'
  # print(URL)
  # sending get request and saving the response as response object
  r = rq.get(url = URL)

  # extracting data in json format
  data = r.json()

  return data

uri = "postgresql://codesmith:TensorFlow01?@cardata.ceq8tkxrvrbb.us-west-2.rds.amazonaws.com:5432/postgres"
engine = create_engine(uri)

table_df = pd.read_sql_table(
    "CarsBidData",
    con=engine
)

# print(table_df.info())

# print(table_df.head())

# vins = table_df["VIN"]
# miles = table_df["Mileage"]

# cardata1 = pd.concat([vins, miles], axis = 1)

cardata2 = table_df[["VIN", "Mileage"]]

# print(cardata1.head())
print(cardata2.head())

responses = []
for index, row in cardata2.iterrows():
  print(index)
  thisVin = row["VIN"]
  print(thisVin)
  apiResponse = getVinInfo(VIN=thisVin)
  print(apiResponse)
  responses.append(apiResponse)
  