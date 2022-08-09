
from datetime import date, datetime
import warnings
import re
import time
from carsandbids_scrape import scrape_listings, scrape_text_from_listing, pull_data_from_listing_text
from vin_api import getVinInfo, process_vin_audit_data
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from sqlalchemy import create_engine
from sqlalchemy import text

uri = "postgresql://codesmith:TensorFlow01?@cardata.ceq8tkxrvrbb.us-west-2.rds.amazonaws.com:5432/postgres"
engine = create_engine(uri)

pull_urls= 'SELECT "URL" FROM "CarsBidData"'
pull_index_CB= 'SELECT index FROM "CarsBidData"'
pull_index_vin_audit= 'SELECT index FROM "VinAuditData"'

with engine.connect() as connection:
    urls = engine.execute(pull_urls).fetchall()
    idx_VA  = engine.execute(pull_index_vin_audit).fetchall()
    idx_CB  = engine.execute(pull_index_CB).fetchall()

urls = [url for (url, ) in urls]

idx_VA = [idx for (idx, ) in idx_VA]
idx_VA = idx_VA[len(idx_VA) - 1]

idx_CB = [idx for (idx, ) in idx_CB]
idx_CB = idx_CB[len(idx_CB) - 1]

try:
    first_page_listings = scrape_listings("/Users/adamgabriellang/Downloads/chromedriver", 0, 0)
    new_listings = list(set(first_page_listings) - set(urls))
except:
    raise ValueError("Failed to access CarsandBids.com")

with engine.connect() as connection:
    while len(new_listings):
        j = 1
        for i in new_listings:

            try:
                car_details, selling_price_details, dougs_notes, model_year, auction_date = scrape_text_from_listing(i,  "/Users/adamgabriellang/Downloads/chromedriver")
                cb_row = pull_data_from_listing_text(car_details, selling_price_details, dougs_notes, model_year, auction_date, i)
                vin = cb_row["VIN"]
                mileage = cb_row["Mileage"]
                sale_date = cb_row["Date"]
            except:
                warnings.warn(f"Unable to pull data from listing {i}")
            
            try:
                vin_audit_data = process_vin_audit_data(VIN = vin, Mileage= mileage, Date= sale_date)
            except:
                warnings.warn(f"Unable to pull data from VinAudit API for VIN {vin}")
            
            car_bids_sql_stmt = text('''INSERT INTO "CarsBidData"
                                        VALUES (:v0, :v01, :v1, :v2, :v3, :v4,
                                                :v5, :v6, :v7, :v8, :v9, :v10, 
                                                :v11, :v12, :v13, :v14, :v15, 
                                                :v16, :v17, :v18, :v19)''')

            try:
                idx_CB += 1
                connection.execute(car_bids_sql_stmt,
                                    v0=idx_CB, v01=idx_CB,  v1= cb_row["Make"], v2=cb_row["Model"], v3=cb_row["Mileage"], v4=cb_row["VIN"],
                                    v5=cb_row["Title Status"], v6=cb_row["Location"], v7=cb_row["Engine"], v8=cb_row["Drivetrain"], v9=cb_row["Transmission"],
                                    v10=cb_row["Body Style"], v11=cb_row["Exterior Color"], v12=cb_row["Interior Color"], v13=cb_row["Price"], 
                                    v14=cb_row["Sold Type"], v15=cb_row["Num Bids"],
                                    v16=cb_row["Y_N_Reserve"], v17=cb_row["Year"],
                                    v18=cb_row["Date"], v19=cb_row["URL"])
            except:
                warnings.warn("Unable add data to CarsBidTable")
            
            vin_audit_sql_stmt = text('''INSERT INTO "VinAuditData"
                                VALUES (:v0, :v1, :v2, :v3, :v4, :v5)''')
            try:
                idx_VA += 1
                connection.execute(vin_audit_sql_stmt,
                                    v0=idx_VA, v1= vin_audit_data["VIN"], v2=vin_audit_data["Market_Value_Mean"], v3=vin_audit_data["Market_Value_Std"], v4=vin_audit_data["Count"],
                                    v5=round(vin_audit_data["Count_Over_Days"], 3))
            except:
                warnings.warn("Unable add data to VinAuditData")
        
        try:
            first_page_listings = scrape_listings("/Users/adamgabriellang/Downloads/chromedriver", j, 0)
            new_listings = list(set(first_page_listings) - set(urls))
            j += 1
        except:
            raise ValueError("Failed to access CarsandBids.com")
            


            
            



