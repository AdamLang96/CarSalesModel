import os
import pandas as pd
from vin_api import process_vin_audit_data
import time
import boto3
s3 = boto3.resource('s3', aws_access_key_id=os.environ["AWS_ACCESS_KEY"], aws_secret_access_key=os.environ["AWS_SECRET_KEY"])
data = pd.read_csv(os.environ["DATA_PATH"])
row_list = []
vin_headers = ["ID", "VIN",
                          "Market_Value_Mean",
                          "Market_Value_Std",
                          "Count",
                          "Count_Over_Days"]
row_list.append(vin_headers)
start = int(os.environ["START"])
stop = int(os.environ["STOP"])

while start <= stop:
    if start % 100 == 0:
        csv = '\n'.join([','.join([str(c) for c in lst]) for lst in row_list])
        s3.Object("carsvininfo", f'vin_{os.environ["START"]}_to_{os.environ["STOP"]}.csv').put(Body=csv)
    id_ = data.loc[start, "ID"]
    vin     = data.loc[start, "VIN"]
    mileage = data.loc[start, "Mileage"]
    date = data.loc[start, "Date"]
    try:
        vin_vals = process_vin_audit_data(vin=vin, mileage=mileage, sale_date=date)
        row_list.append([id_] + list(vin_vals.values()))
        start += 1
        print(vin_vals)
        time.sleep(5)
    except:
        start += 1
        continue
    


csv = '\n'.join([','.join([str(c) for c in lst]) for lst in row_list])
s3.Object("carsvininfo", f'vin_{os.environ["START"]}_to_{os.environ["STOP"]}.csv').put(Body=csv)
