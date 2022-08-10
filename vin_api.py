import requests as rq
from datetime import date, datetime

run_script = False
run_script_2 = False

def getVinInfo(VIN, API_KEY = 'VA_DEMO_KEY', NUM_DAYS = 90, MILEAGE = 'average'):
  # 'average' if none specified
  URL = f'https://marketvalue.vinaudit.com/getmarketvalue.php?key={API_KEY}&vin={VIN}&format=json&period={NUM_DAYS}&mileage={MILEAGE}'
  r = rq.get(url = URL)
  data = r.json()
  return data


def process_vin_audit_data(VIN, Mileage, Date):
  today = date.today()
  today = today.strftime("%m-%d-%Y")
  today = datetime.strptime(today, "%m-%d-%Y")
  sale_date = datetime.strptime(Date, "%m-%d-%Y")
  delta = today - sale_date
  days = delta.days
  if days <= 90:
    num_days = 90
  else:
    num_days = days
  try:
    vin_audit_data = getVinInfo(VIN = VIN, MILEAGE = Mileage, NUM_DAYS = num_days)
    vin_audit_data = {"VIN": vin_audit_data["vin"], "Market_Value_Mean": vin_audit_data["mean"],
                      "Market_Value_Std": vin_audit_data["stdev"], "Count": vin_audit_data["count"],
                      "Count_Over_Days": vin_audit_data["count"] / num_days}
  except:
    vin_audit_data = None
  
  
  return vin_audit_data

