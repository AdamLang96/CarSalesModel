"""Streamlit App

This script allows the user to make predictions on sales prices for cars on CarsAndBids.

"""
from datetime import date
import requests as rq
import plotly.express as px
import streamlit as st
import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine, text
import os
import boto3
from streamlit_option_menu import option_menu
import altair as alt
import time

session = boto3.Session(
    aws_access_key_id = os.environ["ACCESS_KEY"],
    aws_secret_access_key=os.environ["ACCESS_SECRET"],
    region_name = os.environ["REGION"])


@st.cache_data(ttl=259200, max_entries=None)
def get_vin_info(vin, api_key = 'VA_DEMO_KEY', num_days = 90, mileage = 'average'):
    """pulls data from vinaudit api """
    vinaudit_url = f'https://marketvalue.vinaudit.com/getmarketvalue.php?key={api_key}&vin={vin}&format=json&period={num_days}&mileage={mileage}'
    req = rq.get(url = vinaudit_url)
    data = req.json()
    return data


@st.cache_data(ttl=259200, max_entries=None)
def fetch_market_data():
    sp500 = yf.download("^GSPC", start= '2023-2-1', end=str(date.today())) 
    sp500 = pd.DataFrame(sp500)
    sp500 = sp500["Adj Close"].iloc[0]
    return sp500

# name = 'thismod'
s3 = session.resource('s3')
model_list = []
for i in s3.Bucket('carsalesmodel').objects.all():
    model_list.append(i.key)
 
DATA_URI = os.environ["DATA_URI"]
engine = create_engine(DATA_URI)

SERVER_URI = os.environ["SERVER_URI"]

MODEL_SQL_QUERY = 'SELECT DISTINCT "model" FROM "cars_bids_listings";'
MAKE_SQL_QUERY = 'SELECT DISTINCT "make" FROM "cars_bids_listings";'
ENGINE_SQL_QUERY = 'SELECT DISTINCT "engine" FROM "cars_bids_listings";'
TITLE_STATUS_SQL_QUERY = 'SELECT DISTINCT "status" FROM "cars_bids_listings";'
DRIVE_TRAIN_SQL_QUERY = 'SELECT DISTINCT "drivetrain" FROM "cars_bids_listings";'
TRANSMISSION_SQL_QUERY = 'SELECT DISTINCT "transmission" FROM "cars_bids_listings";'
BODYSTYLE_SQL_QUERY = 'SELECT DISTINCT "bodystyle" FROM "cars_bids_listings";'
SOLDTYPE_SQL_QUERY = 'SELECT DISTINCT "soldtype" FROM "cars_bids_listings";'
YNRESERVE_SQL_QUERY = 'SELECT DISTINCT "y_n_reserve" FROM "cars_bids_listings";'
VIN_SQL_QUERY = 'SELECT "vin" FROM "cars_bids_listings" LIMIT 1;'

with engine.connect() as connection:
    make_df = pd.read_sql_query(text(MAKE_SQL_QUERY), con = connection)
    model_df = pd.read_sql_query(text(MODEL_SQL_QUERY), con = connection)
    engine_df = pd.read_sql_query(text(ENGINE_SQL_QUERY), con = connection)
    title_status_df = pd.read_sql_query(TITLE_STATUS_SQL_QUERY, con = connection)
    drive_train_df = pd.read_sql_query(DRIVE_TRAIN_SQL_QUERY, con = connection)
    transmission_df = pd.read_sql_query(TRANSMISSION_SQL_QUERY, con = connection)
    bodyStyle_df = pd.read_sql_query(BODYSTYLE_SQL_QUERY, con=connection)
    soldType_df = pd.read_sql_query(SOLDTYPE_SQL_QUERY, con = connection)
    reserve_df = pd.read_sql_query(YNRESERVE_SQL_QUERY, con = connection)

make_df.sort_values(by='make', inplace=True)
model_df.sort_values(by='model', inplace=True)
engine_df.sort_values(by='engine', inplace=True)
title_status_df.sort_values(by='status', inplace=True)
drive_train_df.sort_values(by='drivetrain', inplace=True)
transmission_df.sort_values(by='transmission', inplace=True)
bodyStyle_df.sort_values(by='bodystyle', inplace=True)
soldType_df.sort_values(by='soldtype', inplace=True)
reserve_df.sort_values(by='y_n_reserve', inplace=True)

st.set_page_config(layout="wide", page_title="Car Sale Value")
headercol1, headercol2 = st.columns(2)
with st.container():
    with headercol1:
        st.markdown("<h1 style='text-align: center; color: black;'>How Much is Your Collector Car Worth?</h1>", unsafe_allow_html=True)
        st.subheader('Use our API and predict a sale price for your vehicle!')
    with headercol2:
        st.image('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTe1SBdlXWtJ96-zcUnN05YMaumzpJ-q2ei-A&usqp=CAU', width=500)
selected_navbar = option_menu(None, ["Predict", "FAQ", "API"], orientation="horizontal")

    
dataset = st.container()
model = st.container()
years = range(1980, 2023)
chart = st.container()

                
if selected_navbar == "FAQ":
    with st.container():
        with st.expander("What is Cars and Bids?"):
            st.write('Cars and Bids is an online enthusiast car sales platform created by the automotive Youtuber Doug DeMuro. Most listings on the platform are sold in auction format.')
        with st.expander("What model is being used to predict sale price?"):
            st.write('We are using a Gradient Boosted Regression Tree to predict sale price')
        with st.expander("How was the data collected?"):
            st.write('All of the past listings from CarsAndBids.com were collected using webscraping via selenium. We collected estimated market price for each vehicle from VinAudit.com as well as overall market conditions at the time of sale via Yahoo Finance')
        with st.expander("How accurate are the predictions?"):
            st.write('On our best model, we obtain an accuracy of about 75% (MSE .75)')
        with st.expander("Can I use this site commercially?"):
            st.write('This site is not intended to be used commercially and should not be used commercially')
        with st.expander("Is the car price prediction sound financial advice?"):
            st.write('No. This is a purely academic exercise; use the model output at your own discretion')

if selected_navbar == "Predict":
    with st.container():
        st.text('CarsAndBids.com is a new auction website for collector cars from the 80s until now. With a rich history of auctions, we wanted to learn if we could predict\nwhich cars would be good deals on the site by using features of the vehicle like Make, Model, Year, Engine (etc.) as well as car market data on the vehicle\nand general market data, we fit a gradient boosted decision tree to predict the selling price of the car. To determine whether its a good deal, we compare the\npredicted sale price against the market average for similar vehicles. Car market data comes from the VinAudit API\n')
        form = st.form(key='uinput')
    with form:
        form_columns = st.columns(4)
        text_arr = [['Make', 'Model', 'Year'], ['Engine', 'Title', 'Drive'], ['Body Style', 'Reserve', 'Transmission'], ['Vin', 'Mileage']]
        options_arr = [[make_df, model_df, years], [engine_df, title_status_df, drive_train_df], [bodyStyle_df, reserve_df, transmission_df]]
        first_make = make_df.iloc[0]["make"]
        columns = []
        for i, col in enumerate(form_columns):
            if i < 3:
                for j in range(len(text_arr[i])):
                    newcol = col.selectbox(text_arr[i][j], options_arr[i][j], key=(i*3)+j, index=0)
                    columns.append(newcol)
            else:
                for j in range(len(text_arr[i])):
                    newcol = col.text_input(text_arr[i][j], key=(i*3)+j)
                    columns.append(newcol)
                newcol = col.selectbox('ML Model', model_list, key=(i*3)+j+1, index=0)
                columns.append(newcol)

    
        sp500 = fetch_market_data()
        
        m = st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #0099ff;
                color:#ffffff;
            }
            div.stButton > button:hover {
                background-color: #00008B;
                color:#ffffff;
                } 
            </style>""", unsafe_allow_html=True)
        
        
        
        button = st.form_submit_button(label="Submit", use_container_width=True)
        
        if button:
            try:
                if not columns[9]:
                    endpoint = f'{SERVER_URI}/predict_streamlit_no_vin'
                    newres= rq.post(endpoint, json={"rows": [{ "make": columns[0],
                                                            "model": columns[1],
                                                            "mileage": columns[10],
                                                            "status": columns[4], 
                                                            "engine":columns[3],
                                                            "drivetrain": columns[5],
                                                            "transmission" :columns[8],
                                                            "bodystyle": columns[6],
                                                            "y_n_reserve":columns[7],
                                                            "year":columns[2],
                                                            'tree_model': columns[11]}]})  
                else:
                    endpoint = f'{SERVER_URI}/predict_streamlit_no_vin'
                    req = get_vin_info(columns[9])
                    with st.spinner('Running Prediction...'):
                        time.sleep(5)
                    newres= rq.post(f'{SERVER_URI}/predict_streamlit', json={"rows": [{ "make": columns[0],
                                                                "model": columns[1],
                                                                "mileage": columns[10],
                                                                "status": columns[4], 
                                                                "engine":columns[3],
                                                                "drivetrain": columns[5],
                                                                "transmission" :columns[8],
                                                                "bodystyle": columns[6],
                                                                "y_n_reserve":columns[7],
                                                                "year":columns[2],
                                                                'market_value_mean': req["mean"], 
                                                                'market_value_std':req['stdev'], 
                                                                'count_over_days':str(float(req['count']) / 90), 
                                                                'Adj Close':sp500,
                                                                'tree_model': columns[11]}]})            
                response = newres.json()
                newres = response[0][0]
                shaps = pd.DataFrame(pd.Series(response[1]))
                shaps = pd.melt(shaps.reset_index(), id_vars=["index"])
                st.subheader('Dollar Contribution of Each Feature to the Predicted Sale Price')
                chart = (
                    alt.Chart(shaps)
                    .mark_bar()
                    .encode(
                    x=alt.X("value", type="quantitative", title="Dollars"),
                    y=alt.Y("index", type="nominal", title="Features"),
                    color=alt.Color("variable", type="nominal", title="", legend=None),
                    order=alt.Order("variable", sort="descending")))
                st.altair_chart(chart, use_container_width=True)
                st.markdown(f"# Predicted Price on CarsAndBids.com: **${round(newres)}**")
            except:
                st.write('Failed to make prediction. Please try again')

api_column1, api_column2, api_column3 = st.columns(3)          
if selected_navbar == "API":
    st.subheader("Our API is free to use and available via a POST request to http://collectorcarpricing.com:8080/predict")
    st.write('The post request must include the following parameters:')
    api_data = { "Name": ['make', 'model', 'mileage', 'status', 'engine', 'bodystyle', 'y_n_reserve','year', 'drivetrain', 'transmission', 'vin'],
                 "Required": ['yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes','yes', 'yes', 'yes', 'yes'],
                 "Data Type": ['string', 'string', 'float', 'string', 'string', 'string', 'string','int', 'string', 'string', 'string'],
                 "Accepted Values": ["Any brand of auto manufacturer. If the brand doesnt exist in the training data make will not contribute to the prediction",
                                    "Any model from an auto manufacturer. If the model doesnt exist in the training data it will use the average price for the chosen make",
                                    "Any positive number (without commas)",
                                    "Clean, Salvage, Other",
                                    "One of the following: (P9, P8, V1, I6, Electric, I2, H6, I3, I5, Flat-2, I4, Flat-4, R6, H4, V6, W8, V2, Flat-6, V8). If not in this list the model will use the average price for the chosen make",
                                    "One of the following: (SUV/Crossover, Hatchback, Convertible, Van/Minivan, Sedan, Wagon, Truck, Coupe)",
                                    "One of the following: (Reserve, No Reserve)",
                                    "Any year from 1980 - present",
                                    "One of the following: (Rear-wheel drive, 4WD/AWD, Front-wheel drive)",
                                    "One of the following: (Manual, Automatic)",
                                    "Any valid VIN number"]}
    st.table(pd.DataFrame(api_data))
    st.subheader('Ex:')
    st.text('''curl -d '{"rows": [{"make": "Porsche","model": "Cayenne","mileage": "167500.0","status": "Clean" , "engine":"3.6L V6","drivetrain": "4WD/AWD","transmission" :"Manual (6-Speed)","bodystyle":" SUV/Crossover", "y_n_reserve":" No Reserve","year":"2012.0", "vin": "5YJSA1DP4CFF00027"}]}' -X POST http://collectorcarpricing.com:8080/predict''')
       

st.write("Developed by Adam Lang and David Kim [Github Repo]('https://github.com/CodeSmithDSMLProjects/CarSalesModel')")
st.write("Contact us at adamglang96@gmail.com and koyykdy@gmail.com")
