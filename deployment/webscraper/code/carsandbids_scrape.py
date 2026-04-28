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


class CarFeatureParser:
    """OOP-style parser for extracting car features from scraped text using regex."""

    MAKE_PATTERN = re.compile(r'Make(.*?)</dd><dt>')
    MAKE_LINK_PATTERN = re.compile(r'(?<=">)[^\n]+(?=>[^\n]*$)')
    MAKE_REMOVE_PATTERN = re.compile(r'</a')

    MODEL_PATTERN = re.compile(r'Model(.*?)</dd><dt>')
    MODEL_LINK_PATTERN = re.compile(r"(?<=href).*")
    MODEL_VALUE_PATTERN = re.compile(r"(?<=).*")
    MODEL_REMOVE_PATTERN = re.compile(r"(?=><).*")

    MILEAGE_PATTERN = re.compile(r'Mileage(.*?)</dd><dt>')
    MILEAGE_DIGITS_PATTERN = re.compile(r"([0-9]+[,.]?[0-9]+)")

    VIN_PATTERN = re.compile(r'VIN(.*?)</dd><dt>')

    TITLE_STATUS_PATTERN = re.compile(r'Title Status(.*?)</dd><dt>')
    TITLE_SALVAGE_PATTERN = re.compile(r'Salvage')
    TITLE_CLEAN_PATTERN = re.compile(r'Clean')

    LOCATION_PATTERN = re.compile(r"\d{5}")

    ENGINE_PATTERN = re.compile(r'Engine(.*?)</dd><dt>')
    ENGINE_VWI_PATTERN = re.compile(r'[VWI]{1}[0-9]{1,2}')
    ENGINE_FLAT_PATTERN = re.compile(r'Flat-[0-9]{1}')
    ENGINE_ELECTRIC_PATTERN = re.compile(r'Electric')
    ENGINE_INLINE_DASH_PATTERN = re.compile(r'Inline-[0-9]{1}')
    ENGINE_INLINE_SPACE_PATTERN = re.compile(r'Inline\s[0-9]{1}')
    ENGINE_SINGLE_MOTOR_PATTERN = re.compile(r'Single Motor')
    ENGINE_DUAL_MOTOR_PATTERN = re.compile(r'Dual Motor')
    ENGINE_TRIPLE_MOTOR_PATTERN = re.compile(r'Triple Motor')
    ENGINE_ROTARY_PATTERN = re.compile(r'Rotary')

    DRIVETRAIN_PATTERN = re.compile(r'Drivetrain(.*?)</dd><dt>')

    TRANSMISSION_PATTERN = re.compile(r'Transmission(.*?)</dd><dt>')
    TRANS_AUTO_PATTERN = re.compile(r'Automatic')
    TRANS_MANUAL_PATTERN = re.compile(r'Manual')

    BODY_STYLE_PATTERN = re.compile(r'Body Style(.*?)</dd><dt>')

    EXTERIOR_COLOR_PATTERN = re.compile(r'Exterior Color(.*?)</dd><dt>')
    INTERIOR_COLOR_PATTERN = re.compile(r'Interior Color(.*?)</dd><dt>')
    COLOR_TRIM_PATTERN = re.compile(r"^\s*")
    COLOR_TRIM_QUESTION_PATTERN = re.compile(r"\s*?")

    SOLD_PRICE_PATTERN = re.compile(r'Sold(.*?)</span></span>')
    BID_PRICE_PATTERN = re.compile(r'Bid(.*?)</span></span>')
    PRICE_DIGITS_PATTERN = re.compile(r"\d+")

    NUM_BIDS_PATTERN = re.compile(r'Bids(.*?)</span></li>')

    DOUGS_NOTES_PATTERN = re.compile(r"no reserve")

    MODEL_YEAR_PATTERN = re.compile(r'[0-9]{4}')

    AUCTION_DATE_PATTERN = re.compile(r"[0-9]{1,2}")

    URL_HREF_PATTERN = re.compile(".*href=")
    URL_EXTRACT_PATTERN = re.compile(r'"([^"]*)"')

    COLOR_PATTERN = re.compile(pattern=r"^\s*")
    COLOR_QUESTION_PATTERN = re.compile(pattern=r"\s*?")

    def __init__(self):
        pass

    def extract_make(self, text_car_details):
        result = self.MAKE_PATTERN.search(text_car_details).group(1)
        result = self.MAKE_LINK_PATTERN.search(result).group(0)
        result = self.MAKE_REMOVE_PATTERN.sub("", result)
        if result == "Stewart &amp; Stevenson":
            result = "Stewart and Stevenson"
        return result

    def extract_title_status(self, string):
        string = str(string)
        if self.TITLE_SALVAGE_PATTERN.search(string):
            val = "Salvage"
        elif self.TITLE_CLEAN_PATTERN.search(string):
            val = "Clean"
        else:
            val = "Other"
        return val

    def extract_engine(self, string):
        string = str(string)
        match = self.ENGINE_VWI_PATTERN.search(string)
        if match:
            val = match.group(0)
        elif self.ENGINE_FLAT_PATTERN.search(string):
            val = self.ENGINE_FLAT_PATTERN.search(string).group(0)
        elif self.ENGINE_ELECTRIC_PATTERN.search(string):
            val = "Electric"
        elif self.ENGINE_INLINE_DASH_PATTERN.search(string):
            val = self.ENGINE_INLINE_DASH_PATTERN.search(string).group(0).split('-')
            val = f"I{val[1]}"
        elif self.ENGINE_INLINE_SPACE_PATTERN.search(string):
            val = self.ENGINE_INLINE_SPACE_PATTERN.search(string).group(0).split(' ')
            val = f"I{val[1]}"
        elif self.ENGINE_SINGLE_MOTOR_PATTERN.search(string):
            val = "Single Motor"
        elif self.ENGINE_DUAL_MOTOR_PATTERN.search(string):
            val = "Dual Motor"
        elif self.ENGINE_TRIPLE_MOTOR_PATTERN.search(string):
            val = "Triple Motor"
        elif self.ENGINE_ROTARY_PATTERN.search(string):
            val = "Rotary"
        else:
            val = "Other"
        return val

    def extract_transmission(self, string):
        string = str(string)
        if self.TRANS_AUTO_PATTERN.search(string):
            val = "Automatic"
        elif self.TRANS_MANUAL_PATTERN.search(string):
            val = "Manual"
        else:
            val = "Other"
        return val

    def extract_model(self, text_car_details):
        result = self.MODEL_PATTERN.search(text_car_details).group(1)
        result = self.MODEL_LINK_PATTERN.search(result).group(0)
        result = self.MODEL_VALUE_PATTERN.search(result).group(0)
        remove = self.MODEL_REMOVE_PATTERN.search(result).group(0)
        result = re.sub("</a" + remove, '', result)
        return result

    def extract_mileage(self, text_car_details):
        result = self.MILEAGE_PATTERN.search(text_car_details).group(1)
        result = self.MILEAGE_DIGITS_PATTERN.search(result)
        result = result.group(0)
        if "," in result:
            result = result.replace(",", "")
        return result

    def extract_vin(self, text_car_details):
        result = self.VIN_PATTERN.search(text_car_details).group(1)
        result = result[::-1]
        result = result.split(">")[0]
        result = result[::-1]
        return result

    def extract_drivetrain(self, text_car_details):
        result = self.DRIVETRAIN_PATTERN.search(text_car_details).group(1)
        result = result[::-1]
        result = result.split(">")[0]
        result = result[::-1]
        return result

    def extract_transmission_detail(self, text_car_details):
        result = self.TRANSMISSION_PATTERN.search(text_car_details).group(1)
        result = result[::-1]
        result = result.split(">")[0]
        result = result[::-1]
        return self.extract_transmission(result)

    def extract_body_style(self, text_car_details):
        result = self.BODY_STYLE_PATTERN.search(text_car_details).group(1)
        result = result[::-1]
        result = result.split(">")[0]
        result = result[::-1]
        return result

    def extract_title_status_detail(self, text_car_details):
        result = self.TITLE_STATUS_PATTERN.search(text_car_details).group(1)
        result = result[::-1]
        result = result.split(">")[0]
        result = result[::-1]
        result = re.sub(r'\([^)]*\)', '', result)
        result = self.extract_title_status(result)
        return result

    def extract_engine_detail(self, text_car_details):
        result = self.ENGINE_PATTERN.search(text_car_details).group(1)
        result = result[::-1]
        result = result.split(">")[0]
        result = result[::-1]
        result = self.extract_engine(result)
        return result

    def extract_location(self, text_car_details):
        match = self.LOCATION_PATTERN.search(text_car_details)
        match = match.group(0)
        return match

    def extract_exterior_color(self, text_car_details):
        result = self.EXTERIOR_COLOR_PATTERN.search(text_car_details).group(1)
        result = result[::-1]
        result = result.split(">")[0]
        result = result[::-1]
        color = self.COLOR_PATTERN.sub(repl="", string=result)
        color = self.COLOR_QUESTION_PATTERN.sub(repl="", string=color)
        return color

    def extract_interior_color(self, text_car_details):
        result = self.INTERIOR_COLOR_PATTERN.search(text_car_details).group(1)
        result = result[::-1]
        result = result.split(">")[0]
        result = result[::-1]
        color = self.COLOR_PATTERN.sub(repl="", string=result)
        color = self.COLOR_QUESTION_PATTERN.sub(repl="", string=color)
        return color

    def extract_sold_price(self, text_selling_price):
        price = self.SOLD_PRICE_PATTERN.search(text_selling_price)
        sell_type = "Sold For"
        if price is None:
            price = self.BID_PRICE_PATTERN.search(text_selling_price)
            sell_type = "Bid To"
        price = price.group(1)
        price = price.split('>')
        price = price[len(price)-1]
        price = ''.join(self.PRICE_DIGITS_PATTERN.findall(price))
        return price, sell_type

    def extract_num_bids(self, text_selling_price):
        bids = self.NUM_BIDS_PATTERN.search(text_selling_price).group(1)
        bids = bids.split('>')
        bids = bids[len(bids)-1]
        return bids

    def check_reserve(self, text_dougs_notes):
        check = self.DOUGS_NOTES_PATTERN.search(text_dougs_notes)
        if check:
            retval = "No Reserve"
        else:
            retval = "Reserve"
        return retval

    def extract_model_year(self, text_model_year):
        year = self.MODEL_YEAR_PATTERN.search(text_model_year).group(0)
        return year

    def extract_auction_date(self, text_auction_date):
        txt = text_auction_date.split(" ")
        month_dict = {"Jan":1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6,
            'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
        month = month_dict[txt[0]]
        num = self.AUCTION_DATE_PATTERN.search(txt[1]).group(0)
        year = str(txt[2])
        date = str(month) + "-" + str(num) + "-" + year
        return date

    def pull_data_from_listing_text(self, text_car_details, text_selling_price, text_dougs_notes,
                                    text_model_year, text_auction_date):
        output_dict = {}

        try:
            output_dict["Make"] = self.extract_make(text_car_details)
        except:
            output_dict["Make"] = None
        try:
            output_dict["Model"] = self.extract_model(text_car_details)
        except:
            output_dict["Model"] = None
        try:
            output_dict["Location"] = self.extract_location(text_car_details)
        except:
            output_dict["Location"] = None
        try:
            output_dict["VIN"] = self.extract_vin(text_car_details)
        except:
            output_dict["VIN"] = None
        try:
            output_dict["Mileage"] = self.extract_mileage(text_car_details)
        except:
            output_dict["Mileage"] = None
        try:
            output_dict["Title Status"] = self.extract_title_status_detail(text_car_details)
        except:
            output_dict["Title Status"] = None
        try:
            output_dict["Engine"] = self.extract_engine_detail(text_car_details)
        except:
            output_dict["Engine"] = None
        try:
            output_dict["Drivetrain"] = self.extract_drivetrain(text_car_details)
        except:
            output_dict["Drivetrain"] = None
        try:
            output_dict["Transmission"] = self.extract_transmission_detail(text_car_details)
        except:
            output_dict["Transmission"] = None
        try:
            output_dict["Body Style"] = self.extract_body_style(text_car_details)
        except:
            output_dict["Body Style"] = None
        try:
            output_dict["Exterior Color"] = self.extract_exterior_color(text_car_details)
        except:
            output_dict["Exterior Color"] = None
        try:
            output_dict["Interior Color"] = self.extract_interior_color(text_car_details)
        except:
            output_dict["Interior Color"] = None
        try:
            price, sold_type = self.extract_sold_price(text_selling_price)
            output_dict["Price"] = price
            output_dict["Sold Type"] = sold_type
        except:
            output_dict["Price"] = None
            output_dict["Sold Type"] = None
        try:
            output_dict["Num Bids"] = self.extract_num_bids(text_selling_price)
        except:
            output_dict["Num Bids"] = None
        try:
            output_dict["Y_N_Reserve"] = self.check_reserve(text_dougs_notes)
        except:
            output_dict["Y_N_Reserve"] = None
        try:
            output_dict["Year"] = self.extract_model_year(text_model_year)
        except:
            output_dict["Year"] = None
        try:
            output_dict["Date"] = self.extract_auction_date(text_auction_date)
        except:
            output_dict["Date"] = None

        return output_dict


class ChromeDriverWrapper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("--headless")
        options.add_argument("window-size=1920x1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--disable-gpu-sandbox')
        options.add_argument("--single-process")
        options.add_argument("--disable-extensions") 
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


def pull_data_from_listing_text(text_car_details, text_selling_price, text_dougs_notes,
                                text_model_year, text_auction_date):
    """Scrapes all information from an individual listing on CarsandBids.com"""
    parser = CarFeatureParser()
    return parser.pull_data_from_listing_text(text_car_details, text_selling_price, text_dougs_notes,
                                           text_model_year, text_auction_date)