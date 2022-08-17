## Run selenium and chrome driver to scrape data from cloudbytes.dev
import time
import json
import os.path
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, datetime
import requests as rq
import warnings
from sqlalchemy import create_engine
from sqlalchemy import text

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = "/opt/chrome/chrome"
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-dev-tools")
chrome_options.add_argument("--no-zygote")
chrome_options.add_argument("--single-process")
chrome_options.add_argument("window-size=2560x1440")
chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")
chrome_options.add_argument("--remote-debugging-port=9222")
#chrome_options.add_argument("--data-path=/tmp/chrome-user-data")
#chrome_options.add_argument("--disk-cache-dir=/tmp/chrome-user-data")
chrome = webdriver.Chrome("/opt/chromedriver", options=chrome_options)


def scrape_listings(driver, page_number, delay_seconds_between_gets):
    """Scrapes all listings from CarsAndBids.com
    arguments:
        path_to_chrome_driver
        page_number
        delay_seconds_between_gets
    """
    if page_number == 0:
        url = "https://carsandbids.com/past-auctions/"
    else:
        url = f"https://carsandbids.com/past-auctions/?page={page_number}"
    time.sleep(delay_seconds_between_gets)
    driver.get(url)
    html_text = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH,
    "/html/body/div/div[2]/div[2]/div/ul[1]"))).get_attribute("innerHTML")
    html_text = html_text.split(" ")
    href_match = re.compile(".*href=")
    cleaned_urls_list = list(filter(href_match.match, html_text)) # Read Note below
    cleaned_urls_list = ''.join(cleaned_urls_list)
    cleaned_urls_list = re.findall(r'"([^"]*)"', cleaned_urls_list)
    cleaned_urls_list = ["https://carsandbids.com" + s for s in cleaned_urls_list]
    return cleaned_urls_list

def scrape_text_from_listing(driver, url):
    """Scrapes all information from an individual listing on CarsandBids.com"""
    driver.get(url)
    car_details = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH,
     "/html/body/div/div[2]/div[5]/div[1]/div[2]"))).get_attribute("innerHTML")
    selling_price = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH,
     "/html/body/div/div[2]/div[3]/div[1]/div/div"))).get_attribute("innerHTML")
    dougs_notes = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH,
     "/html/body/div/div[2]/div[5]/div[1]/div[3]/div[1]/div"))).get_attribute("innerHTML")
    model_year = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH,
     "/html/body/div/div[2]/div[1]/div/div[1]"))).get_attribute("innerHTML")
    auction_date= WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH,
     "/html/body/div/div[2]/div[5]/div[1]/div[6]/div/ul/li[2]/div[2]"))).get_attribute("innerHTML")
    return car_details, selling_price, dougs_notes, model_year, auction_date

def clean_make(text_car_details):
    """Scrapes all information from an individual listing on CarsandBids.com"""
    result = re.search('Make(.*?)</dd><dt>', text_car_details).group(1)
    result = re.sub("</a", '', re.search('(?<=">)[^\n]+(?=>[^\n]*$)', result).group(0))
    return result

def clean_title(string):
    """Scrapes all information from an individual listing on CarsandBids.com"""
    string = str(string)
    if re.search('Salvage', string):
        val = "Salvage"
    elif re.search('Clean', string):
        val = "Clean"
    else:
        val = "Other"
    return val

def clean_engine(string):
    """Scrapes all information from an individual listing on CarsandBids.com"""
    string = str(string)
    if re.search('[A-Z]{1}[0-9]{1}', string):
        val = re.search('[A-Z]{1}[0-9]{1}', string).group(0)
    elif re.search('Flat-[0-9]{1}', string):
        val = re.search('Flat-[0-9]{1}', string).group(0)
    elif re.search('Electric', string):
        val = "Electric"
    else:
        val = "Other"
    return val

def clean_trans(string):
    """Scrapes all information from an individual listing on CarsandBids.com"""
    string = str(string)
    if re.search('Automatic', string):
        val = "Automatic"
    elif re.search('Manual', string):
        val = "Manual"
    else:
        val = "Other"
    return val


def clean_model(text_car_details):
    """Scrapes all information from an individual listing on CarsandBids.com"""
    result = re.search('Model(.*?)</dd><dt>', text_car_details).group(1)
    result = re.search("(?<=href).*", result).group(0)
    result = re.search("(?<=>).*", result).group(0)
    remove = re.search("(?=><).*", result).group(0)
    result = re.sub("</a" + remove, '', result)
    return result

def clean_all_but_make_model_location(text_car_details, keyword):
    """Scrapes all information from an individual listing on CarsandBids.com"""
    result = re.search(f'{keyword}(.*?)</dd><dt>', text_car_details).group(1)
    if keyword == "Mileage":
        reg = re.compile("([0-9]+[,.]?[0-9]+)")
        result = re.search(reg, result)
        result = result.group(0)
        if "," in result:
            result = result.replace(",", "")
            return result
    result = result[::-1]
    result = result.split(">")[0]
    result = result[::-1]
    if keyword == "Title Status":
        result = re.sub(r'\([^)]*\)', '', result)
        result = clean_title(result)
    if keyword == "Engine":
        result = clean_engine(result)
    if keyword == "Transmission":
        result = clean_trans(result)
    return result

def clean_location(text_car_details):
    """Scrapes all information from an individual listing on CarsandBids.com"""
    reg = re.compile(r"\d{5}")
    match = re.search(reg, text_car_details)
    match = match.group(0)
    return match

def get_sold_price(text_selling_price):
    """Scrapes all information from an individual listing on CarsandBids.com"""
    price = re.search('Sold(.*?)</span></span>', text_selling_price)
    sell_type = "Sold For"
    if price is None:
        price = re.search('Bid(.*?)</span></span>', text_selling_price)
        sell_type = "Bid To"
    price = price.group(1)
    price = price.split('>')
    price = price[len(price)-1]
    price = ''.join(re.findall("\d+", price))
    return price, sell_type

def get_num_bids(text_selling_price):
    """Scrapes all information from an individual listing on CarsandBids.com"""
    bids = re.search('Bids(.*?)</span></li>', text_selling_price).group(1)
    bids = bids.split('>')
    bids = bids[len(bids)-1]
    return bids

def check_reserve(text_dougs_notes):
    """Scrapes all information from an individual listing on CarsandBids.com""" 
    check = re.search("no reserve", text_dougs_notes)
    if check:
        retval = "No Reserve"
    else:
        retval = "Reserve"
    return retval

def get_model_year(text_model_year):
    """Scrapes all information from an individual listing on CarsandBids.com"""
    year = re.search(r'[0-9]{4}', text_model_year).group(0)
    return year

def get_auction_date(text_auction_date):
    """Scrapes all information from an individual listing on CarsandBids.com"""
    txt = text_auction_date.split(" ")
    month_dict = {"Jan":1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 
        'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
    month = month_dict[txt[0]]
    reg = re.compile("[0-9]{1,2}")
    num = re.search(reg, txt[1]).group(0)
    year = str(txt[2])
    date = str(month) + "-" + str(num) + "-" + year
    return date

def clean_color(text_color):
    """Scrapes all information from an individual listing on CarsandBids.com"""
    color = re.sub(pattern = r"^\s*", repl = "", string = text_color)
    color = re.sub(pattern = r"\s*?", repl = "", string = color)
    return color

def pull_data_from_listing_text(text_car_details, text_selling_price, text_dougs_notes,
                                text_model_year, text_auction_date):

    """Scrapes all information from an individual listing on CarsandBids.com"""
    keywords = ["Make", "Model", "Mileage", "VIN","Title Status", "Location",
                "Engine", "Drivetrain", "Transmission", "Body Style",
                "Exterior Color", "Interior Color"]
    output_dict = {}

    clean_data_dict = {"Make": clean_make, "Model": clean_model, "Location": clean_location,
                       "VIN": clean_all_but_make_model_location,
                       "Mileage": clean_all_but_make_model_location,
                       "Title Status": clean_all_but_make_model_location,
                       "Engine": clean_all_but_make_model_location,
                       "Drivetrain": clean_all_but_make_model_location,
                       "Transmission": clean_all_but_make_model_location,
                       "Body Style": clean_all_but_make_model_location,
                       "Exterior Color": clean_color,
                       "Interior Color": clean_color}
    for key in keywords:
        func = clean_data_dict[key]
        try:
            if key not in ["Make", "Model", "Location"]:
                output_dict[key] = func(text_car_details, key)
            else:
                output_dict[key] = func(text_car_details)

        except:
            output_dict[key] = None
    try:
        price, sold_type = get_sold_price(text_selling_price)
        output_dict["Price"] = price
        output_dict["Sold Type"] = sold_type
    except:
        output_dict["Price"] = None
        output_dict["Sold Type"] = None
    try:
        output_dict["Num Bids"] = get_num_bids(text_selling_price)
    except:
        output_dict["Num Bids"] = None
    try:
        output_dict["Y_N_Reserve"] = check_reserve(text_dougs_notes)
    except:
        output_dict["Y_N_Reserve"] = None
    try:
        output_dict["Year"] = get_model_year(text_model_year)
    except:
        output_dict["Year"] = None
    try:
        output_dict["Date"] = get_auction_date(text_auction_date)
    except:
        output_dict["Date"] = None

    return output_dict


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



def main():
    URI = """postgresql://codesmith:TensorFlow01?@cardata.ceq8tkxrvrbb.us-west-2.rds.amazonaws.com:5432/postgres"""
    engine = create_engine(URI)

    PULL_URLS= 'SELECT "URL" FROM "CarsBidData"'
    PULL_INDEX_CB= 'SELECT id_ FROM "CarsBidData"'
    PULL_INDEX_VIN_AUDIT= 'SELECT index FROM "VinAuditData"'

    with engine.connect() as connection:
        urls = connection.execute(PULL_URLS).fetchall()
        idx_VA  = connection.execute(PULL_INDEX_VIN_AUDIT).fetchall()
        idx_CB  = connection.execute(PULL_INDEX_CB).fetchall()

    urls = [url for (url, ) in urls]
    idx_VA = [idx for (idx, ) in idx_VA]
    idx_VA = idx_VA[len(idx_VA) - 1]

    idx_CB = [idx for (idx, ) in idx_CB]
    idx_CB = idx_CB[len(idx_CB) - 1]

    try:
        first_page_listings = scrape_listings(chrome, 0, 0)
        new_listings = list(set([item for item in first_page_listings if item not in urls]))
        print(new_listings)
    except:
        raise ValueError("Failed to access CarsandBids.com")

    while len(new_listings) > 0:
        print(len(new_listings))
        j = 1
        k = 1
        for i in new_listings:
            print(k)
            k += 1
            try:
                car_details, selling_price_details, dougs_notes, model_year, auction_date = scrape_text_from_listing(chrome, i)
                cb_row = pull_data_from_listing_text(car_details, selling_price_details, dougs_notes, model_year, auction_date)
                print(cb_row)
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
                
            car_bids_sql_stmt = text('''INSERT INTO "CarsBidData"
                                        VALUES (:v0, :v1, :v2, :v3, :v4,
                                                :v5, :v6, :v7, :v8, :v9, :v10, 
                                                :v11, :v12, :v13, :v14, :v15, 
                                                :v16, :v17, :v18, :v19)''')

            try:
                idx_CB += 1
                with engine.connect() as connection:
                    connection.execute(car_bids_sql_stmt,
                                        v0 = idx_CB,
                                        v1= cb_row["Make"],
                                        v2=cb_row["Model"],
                                        v3=cb_row["Mileage"],
                                        v4=cb_row["VIN"],
                                        v5=cb_row["Title Status"],
                                        v6=cb_row["Location"],
                                        v7=cb_row["Engine"],
                                        v8=cb_row["Drivetrain"],
                                        v9=cb_row["Transmission"],
                                        v10=cb_row["Body Style"],
                                        v11=cb_row["Exterior Color"],
                                        v12=cb_row["Interior Color"],
                                        v13=cb_row["Price"],
                                        v14=cb_row["Sold Type"],
                                        v15=cb_row["Num Bids"],
                                        v16=cb_row["Y_N_Reserve"],
                                        v17=cb_row["Year"],
                                        v18=cb_row["Date"],
                                        v19=cb_row["URL"])
                    
            except:
                warnings.warn("Unable add data to CarsBidTable")
            
            vin_audit_sql_stmt = text('''INSERT INTO "VinAuditData"
                                VALUES (:v0, :v1, :v2, :v3, :v4, :v5)''')
            try:
                idx_VA += 1
                with engine.connect() as connection:
                    connection.execute(vin_audit_sql_stmt,
                                        v0=idx_VA, v1= vin_audit_data["VIN"], v2=vin_audit_data["Market_Value_Mean"], v3=vin_audit_data["Market_Value_Std"], v4=vin_audit_data["Count"],
                                        v5=round(vin_audit_data["Count_Over_Days"], 3))
            except:
                warnings.warn("Unable add data to VinAuditData")
        
        try:
            j += 1
            print(j)
            first_page_listings = scrape_listings(chrome, 0, 0)
            new_listings = list(set([item for item in first_page_listings if item not in urls]))
        except:
            raise ValueError("Failed to access CarsandBids.com")






def handler(event=None, context=None):
    main()
    return {
        "statusCode": 200,
        "ranSuccess" : True
    }