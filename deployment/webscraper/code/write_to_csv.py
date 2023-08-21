from carsandbids_scrape import scrape_listings, pull_data_from_listing_text, scrape_text_from_listing
import time
import os
import boto3
rowlist = []
s3 = boto3.resource('s3', aws_access_key_id=os.environ["AWS_ACCESS_KEY"], aws_secret_access_key=os.environ["AWS_SECRET_KEY"])
field =  ["ID", "Page_Number", "Make", "Model", "Mileage", "VIN", "Title Status",
            "Location",
                                            "Engine",
                                            "Drivetrain",
                                            "Transmission",
                                            "Body Style",
                                            "Exterior Color",
                                            "Interior Color",
                                            "Price",
                                            "Sold Type",
                                            "Num Bids",
                                            "Y_N_Reserve",
                                            "Year",
                                            "Date",
                                            "URL"]
rowlist.append(field)    
k = int(os.environ["START"])
id_ = 0
    # while more_listings:
while k<=int(os.environ["STOP"]):
        # try:
        
            new_listings = scrape_listings(k, 15)
            new_listings = list(set(new_listings))
            for i in new_listings:
                    try:
                        car_details, selling_price_details, dougs_notes, model_year, auction_date = scrape_text_from_listing(i)
                        cb_row = pull_data_from_listing_text(car_details, selling_price_details, dougs_notes, model_year, auction_date)
                        cb_row["URL"] = str(i)
                        write_row = [id_, k, cb_row["Make"],
                        cb_row["Model"],
                        cb_row["Mileage"],
                        cb_row["VIN"],
                        cb_row["Title Status"],
                        cb_row["Location"],
                        cb_row["Engine"],
                        cb_row["Drivetrain"],
                        cb_row["Transmission"],
                        cb_row["Body Style"],
                        cb_row["Exterior Color"],
                        cb_row["Interior Color"],
                        cb_row["Price"],
                        cb_row["Sold Type"],
                        cb_row["Num Bids"],
                        cb_row["Y_N_Reserve"],
                        cb_row["Year"],
                        cb_row["Date"],
                        cb_row["URL"]]
                        rowlist.append(write_row)
                        print('appended')
                        time.sleep(5)
                        id_ += 1
                    except:
                            s3.Object("carscsvs", f'cars_{os.environ["START"]}_to_{os.environ["STOP"]}.csv').put(Body='\n'.join([','.join([str(c) for c in lst]) for lst in rowlist]))
                    #       print('iteration failed')
            k+=1            
s3.Object("carscsvs", f'cars_{os.environ["START"]}_to_{os.environ["STOP"]}.csv').put(Body='\n'.join([','.join([str(c) for c in lst]) for lst in rowlist]))
