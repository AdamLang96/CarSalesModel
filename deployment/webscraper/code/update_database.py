import warnings
import os
from sqlalchemy import create_engine
from sqlalchemy import text
from carsandbids_scrape import scrape_listings
from carsandbids_scrape import pull_data_from_listing_text, scrape_text_from_listing
from vin_api import process_vin_audit_data

def main():
    URI = os.environ["URI"]
    engine = create_engine(URI)

    PULL_URLS= text('SELECT "url" FROM "cars_bids_listings"')
    everything= text('SELECT * FROM "cars_bids_listings"')
    with engine.connect() as connection:
         urls = connection.execute(everything).fetchall()
    
    PULL_INDEX_CB= text('SELECT "id" FROM "cars_bids_listings"')
    PULL_INDEX_VIN_AUDIT= text('SELECT "id" FROM "vin_audit_data"')

    with engine.connect() as connection:
        urls = connection.execute(PULL_URLS).fetchall()
        idx_VA  = connection.execute(PULL_INDEX_VIN_AUDIT).fetchall()
        idx_CB  = connection.execute(PULL_INDEX_CB).fetchall()

    urls = [url for (url, ) in urls]

    idx_VA = [idx for (idx, ) in idx_VA]
    if idx_VA == []:
        idx_VA = [0]
    idx_VA = idx_VA[len(idx_VA) - 1]

    idx_CB = [idx for (idx, ) in idx_CB]
    if idx_CB == []:
        idx_CB = [0]
    idx_CB = idx_CB[len(idx_CB) - 1]
    
    more_listings = True
    k = 0
    while more_listings:
            first_page_listings = scrape_listings(k, 0)
            new_listings = [item for item in first_page_listings if item not in urls]
            new_listings = list(set(new_listings))
            if not len(new_listings):
                more_listings = False
                print('done')
            for i in new_listings:
                try:
                    car_details, selling_price_details, dougs_notes, model_year, auction_date = scrape_text_from_listing(i)
                    cb_row = pull_data_from_listing_text(car_details, selling_price_details, dougs_notes, model_year, auction_date)
                    cb_row["URL"] = str(i)
                    vin = cb_row["VIN"]
                    mileage = cb_row["Mileage"]
                    sale_date = cb_row["Date"]
                except:
                    warnings.warn(f"Unable to pull data from listing {i}")
                
                try:
                    vin_audit_data = process_vin_audit_data(vin = vin, mileage= mileage, sale_date= sale_date)
                except:
                    warnings.warn(f"Unable to pull data from VinAudit API for VIN {vin}")
                    
                car_bids_sql_stmt = text('''INSERT INTO "cars_bids_listings"
                                            VALUES (:v0, :v1, :v2, :v3, :v4,
                                                    :v5, :v6, :v7, :v8, :v9, :v10, 
                                                    :v11, :v12, :v13, :v14, :v15, 
                                                    :v16, :v17, :v18, :v19)''')
                
                idx_CB = int(idx_CB) + 1
                with engine.connect() as connection:
                    print(cb_row)
                    connection.execute(car_bids_sql_stmt,
                                        v0  = str(idx_CB),
                                        v1  = cb_row["Make"],
                                        v2  = cb_row["Model"],
                                        v3  = cb_row["Mileage"],
                                        v4  = cb_row["VIN"],
                                        v5  = cb_row["Title Status"],
                                        v6  = cb_row["Location"],
                                        v7  = cb_row["Engine"],
                                        v8  = cb_row["Drivetrain"],
                                        v9  = cb_row["Transmission"],
                                        v10 = cb_row["Body Style"],
                                        v11 = cb_row["Exterior Color"],
                                        v12 = cb_row["Interior Color"],
                                        v13 = cb_row["Price"],
                                        v14 = cb_row["Sold Type"],
                                        v15 = cb_row["Num Bids"],
                                        v16 = cb_row["Y_N_Reserve"],
                                        v17 = cb_row["Year"],
                                        v18 = cb_row["Date"],
                                        v19 = cb_row["URL"])
                    print('insert to cars complete')

                # except:
                warnings.warn("Unable add data to carsandbidsdata")
                
                vin_audit_sql_stmt = text('''INSERT INTO "vin_audit_data" 
                                            VALUES (:v0, :v1, :v2, :v3, :v4, :v5)''')
                try:
                    idx_VA += 1
                    with engine.connect() as connection:
                
                        connection.execute(vin_audit_sql_stmt,
                                            v0=str(idx_VA), v1= vin_audit_data["VIN"], v2=vin_audit_data["Market_Value_Mean"], v3=vin_audit_data["Market_Value_Std"], v4=vin_audit_data["Count"],
                                            v5=vin_audit_data["Count_Over_Days"])
                        
                        print('insert to vin_audit_data complete')

                except:
                    warnings.warn("Unable add data to VinAuditData")
            k+=1
            
        
if __name__ == "__main__":
    main()
        



