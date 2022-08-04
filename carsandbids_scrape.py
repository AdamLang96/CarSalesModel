import numpy as np
import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

#"/Users/adamgabriellang/Downloads/chromedriver"

def scrape_listings(path_to_chrome_driver,  num_pages):
    total_urls = []
    urls = ["https://carsandbids.com/past-auctions/"]
    urls_2 = [f"https://carsandbids.com/past-auctions/?page={i}" for i in range(2,num_pages)]
    urls = urls + urls_2
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(path_to_chrome_driver, options=options)
    for url in urls:
        driver.get(url)
        html_text = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div/div[2]/div[2]/div/ul[1]"))).get_attribute("innerHTML")
        html_text = html_text.split(" ")
        href_match = re.compile(".*href=")
        cleaned_urls_list = list(filter(href_match.match, html_text)) # Read Note below
        cleaned_urls_list = ''.join(cleaned_urls_list)
        cleaned_urls_list = re.findall(r'"([^"]*)"', cleaned_urls_list)
        cleaned_urls_list = ["https://carsandbids.com" + s for s in cleaned_urls_list]
        total_urls = total_urls + cleaned_urls_list
    return total_urls


#https://carsandbids.com/auctions/rkbZo4bO/1987-mercedes-benz-560sec


#xpath for data 
  # /html/body/div/div[2]/div[5]/div[1]/div[2]

# url ="https://carsandbids.com/auctions/rkbZo4bO/1987-mercedes-benz-560sec"



with open('test_text.txt') as f:
    text = f.read()



def pull_data_from_listing(text):

    def clean_make(text):
        result = re.search('Make(.*?)</dd><dt>', text).group(1)
        result = re.sub("</a", '', re.search('(?<=">)[^\n]+(?=>[^\n]*$)', result).group(0))
        return result
    def clean_model(text):
        result = re.search('Model(.*?)</dd><dt>', text).group(1)
        result = re.search("(?<=href).*", result).group(0)
        result = re.search("(?<=>).*", result).group(0)
        remove = re.search("(?=><).*", result).group(0)
        result = re.sub("</a" + remove, '', result)
        return result
    def clean_all_but_make_model_location(text, keyword):
        result = re.search(f'{keyword}(.*?)</dd><dt>', text).group(1)
        result = result[::-1]
        result = result.split(">")[0]
        result = result[::-1]
        return result
    def clean_location(text):
        reg = re.compile('^.*(?P<zipcode>\d{5}).*$')
        match = reg.match(text)
        match = match.groupdict()
        return match["zipcode"]

    keywords = ["Make", "Model", "Mileage", "VIN","Title Status", "Location"
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
            output_dict[key] = f(text)
        except:
            output_dict[key] = None

    return output_dict







        


