import numpy as np
import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
pages = [f"https://carsandbids.com/past-auctions/?page={i}" for i in range(2,167)]
test_uri = pages[0]
print(test_uri)
#makes get request
html_data = rq.get(test_uri)

#pass get request into bs4

soup = BeautifulSoup(html_data.text, 'html.parser')
print(soup.prettify())

auctions = soup.find_all("div", class_="col primary full")

# print(auctions)# 'auctions-list past-auctions '


