"""CarsandBids.com data scraper
This script scrapes data from past auctions off of CarsandBids.com
"""
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CHROMEDRIVER_LOCATION = "/bin/chromedriver"
CHROME_HEADLESS_LOCATION = "/bin/headless-chromium"

class ChromeDriverWrapper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        options.binary_location = CHROME_HEADLESS_LOCATION
        options.add_argument("--headless")
        options.add_argument("window-size=1920x1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        # options.add_argument("start-maximized")
        # options.add_argument("enable-automation")
        # options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--disable-gpu-sandbox')
        options.add_argument("--single-process")
        options.add_argument("--disable-extensions") 
        # options.add_argument('--remote-debugging-port=9222')
        options.add_argument(
            '"user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"')
        self._driver = webdriver.Chrome(options=options, executable_path=CHROMEDRIVER_LOCATION)

    def get_url(self, url):
        self._driver.get(url)

    def get_title(self):
        return self._driver.title

    def close(self):
        self._driver.quit()


def scrape_listings(page_number, delay_seconds_between_gets):
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
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
   
    driver = ChromeDriverWrapper()
    time.sleep(delay_seconds_between_gets)
    driver.get_url(url)
    html_text = WebDriverWait(driver._driver, 5).until(EC.visibility_of_element_located((By.XPATH,
    "/html/body/div/div[2]/div[2]/div/ul[1]"))).get_attribute("innerHTML")
    html_text = html_text.split(" ")
    href_match = re.compile(".*href=")
    cleaned_urls_list = list(filter(href_match.match, html_text)) # Read Note below
    cleaned_urls_list = ''.join(cleaned_urls_list)
    cleaned_urls_list = re.findall(r'"([^"]*)"', cleaned_urls_list)
    cleaned_urls_list = ["https://carsandbids.com" + s for s in cleaned_urls_list]
    return cleaned_urls_list

def scrape_text_from_listing(url):
    """Scrapes all information from an individual listing on CarsandBids.com"""
   
    driver = ChromeDriverWrapper()
    driver.get_url(url)
    car_details = WebDriverWait(driver._driver, 5).until(EC.visibility_of_element_located((By.XPATH,
     "/html/body/div/div[2]/div[5]/div[1]/div[2]"))).get_attribute("innerHTML")
    selling_price = WebDriverWait(driver._driver, 5).until(EC.visibility_of_element_located((By.XPATH,
     "/html/body/div/div[2]/div[3]/div[1]/div/div"))).get_attribute("innerHTML")
    dougs_notes = WebDriverWait(driver._driver, 5).until(EC.visibility_of_element_located((By.XPATH,
     "/html/body/div/div[2]/div[5]/div[1]/div[3]/div[1]/div"))).get_attribute("innerHTML")
    model_year = WebDriverWait(driver._driver, 5).until(EC.visibility_of_element_located((By.XPATH,
     "/html/body/div/div[2]/div[1]/div/div[1]"))).get_attribute("innerHTML")
    auction_date= WebDriverWait(driver._driver, 5).until(EC.visibility_of_element_located((By.XPATH,
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
        # except error_1_from_func:
        #   handle this case
        # except error_2_from_func:
        #   handle this case
        # ...
        # else:
        #   default behavior
        # finally:
        #   if func(text_car_details)
        #   if not output_dict[key]:
        #       output_dict[key] = None
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
