import numpy as np
import pandas as pd
import requests as rq
import sqlalchemy as sa
from bs4 import BeautifulSoup

def getVinInfo(API_KEY = 'VA_DEMO_KEY', VIN = 'WDBUF65J64A534963', NUM_DAYS = 90, MILEAGE = 30000):
  # 'average' if none specified
  URL = f'https://marketvalue.vinaudit.com/getmarketvalue.php?key={API_KEY}&vin={VIN}&format=json&period={NUM_DAYS}&mileage={MILEAGE}'
  # print(URL)
  # sending get request and saving the response as response object
  r = rq.get(url = URL)

  # extracting data in json format
  data = r.json()

  return data

