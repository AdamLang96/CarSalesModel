import numpy as np
import pandas as pd
import requests as rq
import re
import time
import pickle as pkl
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from sqlalchemy import create_engine


run_script = False


with open("color_dict.pkl", 'rb') as f:
    color_dict = pkl.load(f)

color_dict = {k.lower(): v for k, v in color_dict.items()}


#"/Users/adamgabriellang/Downloads/chromedriver"

def scrape_listings(path_to_chrome_driver, num_pages, delay_seconds_between_gets):
    #check to see if there are any listings
    total_urls = []
    urls = ["https://carsandbids.com/past-auctions/"]
    urls_2 = [f"https://carsandbids.com/past-auctions/?page={i}" for i in range(2,num_pages)]
    urls = urls + urls_2
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    s = Service(path_to_chrome_driver)
    driver = webdriver.Chrome(service=s, options=options)
    i=0
    for url in urls:
        print(f"listing page: {i} ")
        i+=1
        time.sleep(delay_seconds_between_gets)
        driver.get(url)
        html_text = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div/div[2]/div[2]/div/ul[1]"))).get_attribute("innerHTML")
        html_text = html_text.split(" ")
        href_match = re.compile(".*href=")
        cleaned_urls_list = list(filter(href_match.match, html_text)) # Read Note below
        cleaned_urls_list = ''.join(cleaned_urls_list)
        cleaned_urls_list = re.findall(r'"([^"]*)"', cleaned_urls_list)
        cleaned_urls_list = ["https://carsandbids.com" + s for s in cleaned_urls_list]
        total_urls = total_urls + cleaned_urls_list
    total_urls = list(set(total_urls))
    return total_urls


def scrape_text_from_listing(url, path_to_chrome_driver):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    s = Service(path_to_chrome_driver)
    driver = webdriver.Chrome(service=s, options=options)
    driver.get(url)
    html_text_car_details = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div/div[2]/div[5]/div[1]/div[2]"))).get_attribute("innerHTML")
    html_text_selling_price_details = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div/div[2]/div[3]/div[1]/div/div"))).get_attribute("innerHTML")
    html_text_dougs_notes = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div/div[2]/div[5]/div[1]/div[3]/div[1]/div"))).get_attribute("innerHTML")
    html_text_model_year_details = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div/div[2]/div[1]/div/div[1]"))).get_attribute("innerHTML")
    return html_text_car_details, html_text_selling_price_details, html_text_dougs_notes, html_text_model_year_details


def pull_data_from_listing_text(text_car_details, text_selling_price, text_dougs_notes, text_model_year):

    def clean_make(text_car_details):
        result = re.search('Make(.*?)</dd><dt>', text_car_details).group(1)
        result = re.sub("</a", '', re.search('(?<=">)[^\n]+(?=>[^\n]*$)', result).group(0))
        return result
    def clean_model(text_car_details):
        result = re.search('Model(.*?)</dd><dt>', text_car_details).group(1)
        result = re.search("(?<=href).*", result).group(0)
        result = re.search("(?<=>).*", result).group(0)
        remove = re.search("(?=><).*", result).group(0)
        result = re.sub("</a" + remove, '', result)
        return result
    def clean_all_but_make_model_location(text_car_details, keyword):
        result = re.search(f'{keyword}(.*?)</dd><dt>', text_car_details).group(1)
        result = result[::-1]
        result = result.split(">")[0]
        result = result[::-1]
        return result
    def clean_location(text_car_details):
        reg = re.compile('^.*(?P<zipcode>\d{5}).*$')
        match = reg.match(text_car_details)
        match = match.groupdict()
        return match["zipcode"]

    def get_sold_price(text_selling_price):
        price = re.search('Sold(.*?)</span></span>', text_selling_price)
        sell_type = "Sold For"
        if price == None:
            price = re.search('Bid(.*?)</span></span>', text_selling_price)
            sell_type = "Bid To"
        price = price.group(1)
        price = price.split('>')
        price = price[len(price)-1]
        price = ''.join(re.findall("\d+", price))
        return price, sell_type
    def get_num_bids(text_selling_price):
        bids = re.search('Bids(.*?)</span></li>', text_selling_price).group(1)
        bids = bids.split('>')
        bids = bids[len(bids)-1]
        return bids
    def check_reserve(text_dougs_notes):    
        check = re.search("no reserve", text_dougs_notes)
        if check:
            return "No Reserve"
        else:
            return "Reserve"
    def get_model_year(text_model_year):
        year = re.search(r'[0-9]{4}', text_model_year).group(0)
        return year

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
                       "Exterior Color": clean_all_but_make_model_location,
                       "Interior Color": clean_all_but_make_model_location}
    for key in keywords:
        f = clean_data_dict[key]
        try:
            if key not in ["Make", "Model", "Location"]:    
                output_dict[key] = f(text_car_details, key)
            else:
                output_dict[key] = f(text_car_details)
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


    return output_dict






if run_script:
    data = []
    listings = scrape_listings("/Users/adamgabriellang/Downloads/chromedriver", 167, 0)
    i = 1
    j = 1
    for url in listings:
        time.sleep(0)
        try:
            html_text_car_details, html_text_selling_price_details, html_text_dougs_notes, html_text_model_year_details = scrape_text_from_listing(url, "/Users/adamgabriellang/Downloads/chromedriver")
            text = pull_data_from_listing_text(html_text_car_details, html_text_selling_price_details, html_text_dougs_notes, html_text_model_year_details)
            data.append(text)
            print(f"finished iteration {i}")
        except:
            print(f"failed to make request for {j}th time")
            j+=1
        i += 1 
    data = pd.DataFrame(data)
    data.to_csv("listings_data.csv")



data = pd.read_csv("listings_data.csv")
data.rename(columns={"Title Status" : "TitleStatus",
             "Body Style": "BodyStyle",
             "Exterior Color": "ExteriorColor",
             "Interior Color": "InteriorColor",
             "Sold Type": "SoldType",
             "Num Bids": "NumBids"}, inplace=True)

data.drop(columns= "Unnamed: 0", inplace=True)
data.to_csv("listings_data_new.csv", index=False)