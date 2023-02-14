"""Streamlit App

This script allows the user to make predictions on sales prices for cars on CarsAndBids.

"""
from datetime import date
import pickle
import requests as rq
import plotly.express as px
import streamlit as st
import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine, text
import os
import boto3
from streamlit_option_menu import option_menu

session = boto3.Session(
    aws_access_key_id = "AKIAUH63BSS4PNGLHLFR",
    aws_secret_access_key="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",
    region_name = 'us-west-2'
)

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
 
name = 'thismod'    
mod = pickle.loads(s3.Bucket("carsalesmodel").Object(f'{name}.pkl').get()['Body'].read())

# URI = os.environ["URI"]

engine = create_engine('postgresql+psycopg2://postgres:postgres@classical-project.ceq8tkxrvrbb.us-west-2.rds.amazonaws.com/postgres')

# URL = 'http://ec2-52-24-15-52.us-west-2.compute.amazonaws.com:8080/predict_streamlit'
URL = 'http://127.0.0.1:5000/predict_streamlit'


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
    vin = pd.read_sql_query(VIN_SQL_QUERY, con = connection)
    
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
        with st.expander("What model are you guys using?"):
            st.write('Tree based model')
        with st.expander("How was the data collected?"):
            st.write('Sold listings are scraped from the website using selenium.')
        with st.expander("How accurate are the predictions?"):
            st.write('MSE of roughly 0.75')
        with st.expander("Can I use this site commercially?"):
            st.write('No.')
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
        columns = []
        for i, col in enumerate(form_columns):
            if i < 3:
                for j in range(len(text_arr[i])):
                    newcol = col.selectbox(text_arr[i][j], options_arr[i][j], key=(i*3)+j)
                    columns.append(newcol)
            else:
                for j in range(len(text_arr[i])):
                    newcol = col.text_input(text_arr[i][j], key=(i*3)+j)
                    columns.append(newcol)
                newcol = col.selectbox('Model', model_list, key=(i*3)+j+1)
                columns.append(newcol)
                
        sp500 = fetch_market_data()
        button = st.form_submit_button(label="Submit", use_container_width=True)
        
        if button:
            # req = get_vin_info(columns[9])
            req = {"mean":20000, 'stdev':123, 'count':123}
            newres= rq.post(URL, json={"rows": [{   "make": columns[0],
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
            newres = response[0]
            shaps = response[1]
            st.write(shaps)
            if newres >= float(req["mean"]):
                SELLSTRING = "recommended"
            else:
                SELLSTRING = 'not recommended'
            st.write(f"Predicted Price on CarsAndBids.com: ${round(newres)}")
            st.write(f"It is {SELLSTRING} that you sell your car on CarsAndBids.com")

api_column1, api_column2, api_column3 = st.columns(3)          
if selected_navbar == "API":
        st.title("Our API is free to use and available at collectorcarpricing.com/predict")
        st.text('''Our API requires you send a JSON object with the key 'rows' 
        and a correspond array of dictionaries with the following keys''')
        with api_column1:
            with st.expander("make"):
                st.write('Make of the car')
            with st.expander("model"):
                st.write('Model of the car')
            with st.expander("mileage"):
                st.write('Number of miles on the car')
            with st.expander("status"):
                st.write('Title status (Clean, Salvage, Other)')
            with st.expander("engine"):
                st.write('Type of Engine (View options in the Predict section of the website)')
                
        with api_column2:
            with st.expander("bodystyle"):
                st.write('Body style (View options in the Predict section of the website)')
            with st.expander("y_n_reserve"):
                st.write('Whether you will list the car with a reserve or not (Reserve, No Reserve)')
            with st.expander("year"):
                st.write('Year the car was produced')
            with st.expander("drivetrain"):
                st.write('Drivetrain of the car (View options in the Predict section of the website)')
            with st.expander("transmission"):
                st.write('Transmission on car (View options in the Predict section of the website)')
        
        with api_column3:
            with st.expander("vin"):
                st.write('Vin # on car')
         

# if selected_navbar == "Model":
#         with model:
#             st.header('Training Loss')
#         with chart:
#                 graph = mod
#                 print(mod)
#                 y = (graph[1].train_score_ / max(graph[1].train_score_ ))
#                 x = range(0, graph[1].train_score_.shape[0])
#                 plt = px.scatter(x=x, y=y, labels=dict(x="N_estimators", y="Loss (%)"))
#                 st.plotly_chart(plt)

st.write("Developed by Adam Lang and David Kim [Github Repo]('https://github.com/CodeSmithDSMLProjects/CarSalesModel')")
