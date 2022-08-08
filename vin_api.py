from ast import Num
import datetime
from xmlrpc.client import DateTime
import numpy as np
import pandas as pd
import requests as rq
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, VARCHAR, Numeric
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date, datetime
import pickle as pkl

run_script = False
run_script_2 = False

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
    con=engine)




cardata = table_df[["VIN", "Mileage", "Date"]]




vin_audit_info = []
failed_vins = []
today = date.today()
d1 = today.strftime("%m-%d-%Y")
d1 = datetime.strptime(d1, "%m-%d-%Y")

i=1
j=1
if run_script:
  for index, row in cardata.iterrows():
    vin = row["VIN"]
    miles = row["Mileage"]
    sale_date = row["Date"]
    d2 = datetime.strptime(sale_date, "%m-%d-%Y")
    delta = d1-d2
    days = delta.days
    if days <= 90:
      num_days = 90
    else:
      num_days = days
    try:
      vin_audit_data = getVinInfo(VIN=vin, MILEAGE=miles, NUM_DAYS=num_days)
      vin_audit_info.append(vin_audit_data)
      print(f"finished iteration {j}")
      j += 1
    except:
      print(f"failed vinaudit request for {i}th time")
      failed_vins.append(vin)
      i += 1


  with open("vinauditobjects.pkl", 'wb') as f:
    pkl.dump(vin_audit_info, f)

  with open("failed_vins.pkl", 'wb') as f:
    pkl.dump(failed_vins, f)
  


#Model - Sparse <- encode car type, year made, etc. 
#Engine - <-  standardizable metrics like combustion volume and cylinder count, horsepower/kWh, electric (binary)
#Transmission 4WD/AWD,Manual <- Manual/Automatic  RWD, FWD (4wd is both)
#Location - Sparse (target encoding)

with open("vinauditobjects.pkl", "rb") as f:
  data = pkl.load(f)


# divisor = num_days
# if divisor <= 90:
#   divisor = 90
# count_normalized = count/divisor
if run_script_2:
  date_data = table_df[["VIN", "Date"]]
  num_days = []
  for index, row in date_data.iterrows():
      vin = row["VIN"]
      sale_date = row["Date"]
      d2 = datetime.strptime(sale_date, "%m-%d-%Y")
      delta = d1-d2
      days = delta.days
      if days <= 90:
        days = 90
      num_days.append({"VIN": vin, "Num_Days": days})

  num_days = pd.DataFrame(num_days)
  num_days.to_csv("days_since_sale_by_vin.csv")


  ### clean vin_audit
  clean_vin_audit = []
  for audit in data:
      if audit['success']:
        clean_vin_audit.append({"VIN": audit["vin"], "Market_Value_Mean": audit["mean"],
                              "Market_Value_Std": audit["stdev"], "Count": audit["count"]})

  clean_vin_audit = pd.DataFrame(clean_vin_audit)
  clean_vin_audit.to_csv("clean_vin_data.csv")

# drops = cardata.duplicated(subset="VIN", keep=False)
# drop_vins = pd.concat([cardata["VIN"], drops], axis=1)


days_since_sale = pd.read_csv("days_since_sale_by_vin.csv")
clean_vin_data = pd.read_csv("clean_vin_data.csv")
merged_vin_data = days_since_sale.merge(clean_vin_data, on="VIN", how="inner")
merged_vin_data = merged_vin_data.drop_duplicates(subset="VIN")

merged_vin_data = merged_vin_data[["VIN", "Num_Days", "Market_Value_Mean", "Market_Value_Std", "Count"]]
merged_vin_data["Count_Over_Days"] = merged_vin_data["Count"] / merged_vin_data["Num_Days"] # Math.max(90, Num_Days)
merged_vin_data.to_csv("full_vin_audit_data.csv")


# responses = []
# for index, row in cardata2.iterrows():
#   print(index)
#   thisVin = row["VIN"]
#   print(thisVin)
#   apiResponse = getVinInfo(VIN=thisVin)
#   print(apiResponse)
#   responses.append(apiResponse)
  
