"""Vin_Api App

Runs Vin_Api

"""
from datetime import date, datetime
import requests as rq

RUN_SCRIPT = False
RUN_SCRIPT_2 = False

def get_vin_info(vin, api_key = 'VA_DEMO_KEY', num_days = 90, mileage = 'average'):
    """pulls data from vinaudit api """
    vinaudit_url = f'https://marketvalue.vinaudit.com/getmarketvalue.php?key={api_key}&vin={vin}&format=json&period={num_days}&mileage={mileage}'
    req = rq.get(url = vinaudit_url)
    data = req.json()
    return data


def process_vin_audit_data(vin, mileage, sale_date):
    """proccesses data from vinaudit api """
    today = date.today()
    today = today.strftime("%m-%d-%Y")
    today = datetime.strptime(today, "%m-%d-%Y")
    sale_date = datetime.strptime(sale_date, "%m-%d-%Y")
    delta = today - sale_date
    days = delta.days
    if days <= 90:
        num_days = 90
    else:
        num_days = days
    try:
        vin_audit_data = get_vin_info(vin = vin, mileage = mileage, num_days = num_days)
        vin_audit_data = {"VIN": vin_audit_data["vin"],
                          "Market_Value_Mean": vin_audit_data["mean"],
                          "Market_Value_Std": vin_audit_data["stdev"],
                          "Count": vin_audit_data["count"],
                          "Count_Over_Days": vin_audit_data["count"] / num_days}
    except:
        vin_audit_data = None
    return vin_audit_data
