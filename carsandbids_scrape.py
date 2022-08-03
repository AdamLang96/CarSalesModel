import numpy as np
import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

pages = [f"https://carsandbids.com/past-auctions/?page={i}" for i in range(2,167)]
test_uri = pages[0]

options = webdriver.ChromeOptions()
options.add_argument('headless')

driver = webdriver.Chrome("/Users/adamgabriellang/Downloads/chromedriver", options=options)
driver.get(test_uri)

text = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div/div[2]/div[2]/div/ul[1]"))).get_attribute("innerHTML")
text = text.split(" ")
r = re.compile(".*href=")
newlist = list(filter(r.match, text)) # Read Note below
newerlist = ''.join(newlist)
stringkeep = re.findall(r'"([^"]*)"', newerlist)




