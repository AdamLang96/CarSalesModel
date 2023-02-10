"""Streamlit App

This script allows the user to make predictions on sales prices for cars on CarsAndBids.

"""
import datetime
import pickle
import requests as rq
import plotly.express as px
import streamlit as st
import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine
from deployment.lambda_webscraper.vin_api import get_vin_info
import os

URI = os.environ["URI"]

engine = create_engine(URI)

URL = 'http://ec2-54-185-209-122.us-west-2.compute.amazonaws.com:8080/predict'

sp500 = yf.download("^GSPC", start= '2019-1-1', end= str(datetime.date.today()))
sp500 = sp500["Adj Close"].iat[-1]

MODEL_SQL_QUERY = 'SELECT DISTINCT "Model" FROM "CarsBidData";'
MAKE_SQL_QUERY = 'SELECT DISTINCT "Make" FROM "CarsBidData";'
ENGINE_SQL_QUERY = 'SELECT DISTINCT "Engine" FROM "CarsBidData";'
TITLE_STATUS_SQL_QUERY = 'SELECT DISTINCT "Title Status" FROM "CarsBidData";'
DRIVE_TRAIN_SQL_QUERY = 'SELECT DISTINCT "Drivetrain" FROM "CarsBidData";'
TRANSMISSION_SQL_QUERY = 'SELECT DISTINCT "Transmission" FROM "CarsBidData";'
BODYSTYLE_SQL_QUERY = 'SELECT DISTINCT "Body Style" FROM "CarsBidData";'
SOLDTYPE_SQL_QUERY = 'SELECT DISTINCT "Sold Type" FROM "CarsBidData";'
YNRESERVE_SQL_QUERY = 'SELECT DISTINCT "Y_N_Reserve" FROM "CarsBidData";'
VIN_SQL_QUERY = 'SELECT "VIN" FROM "CarsBidData" LIMIT 1;'


with engine.connect() as connection:
    make_df = pd.read_sql_query(MAKE_SQL_QUERY, con = connection)
    model_df = pd.read_sql_query(MODEL_SQL_QUERY, con = connection)
    engine_df = pd.read_sql_query(ENGINE_SQL_QUERY, con = connection)
    title_status_df = pd.read_sql_query(TITLE_STATUS_SQL_QUERY, con = connection)
    drive_train_df = pd.read_sql_query(DRIVE_TRAIN_SQL_QUERY, con = connection)
    transmission_df = pd.read_sql_query(TRANSMISSION_SQL_QUERY, con = connection)
    bodyStyle_df = pd.read_sql_query(BODYSTYLE_SQL_QUERY, con=connection)
    soldType_df = pd.read_sql_query(SOLDTYPE_SQL_QUERY, con = connection)
    reserve_df = pd.read_sql_query(YNRESERVE_SQL_QUERY, con = connection)
    vin = pd.read_sql_query(VIN_SQL_QUERY, con = connection)


header = st.container()
dataset = st.container()
model = st.container()
years = range(1980, 2023)
chart = st.container()

with header:
    st.title('CarsAndBids Sale Price Projection')

with dataset:
    st.header('Input Car Details')
    display = st.columns(1)
    make_option = st.selectbox('MAKER', make_df)
    model_option = st.selectbox('Model', model_df)
    year_option = st.selectbox("Year", years)
    engine_option = st.selectbox('Engine', engine_df)
    title_option = st.selectbox('Title', title_status_df)
    drive_option = st.selectbox('Drive', drive_train_df)
    transmission_option = st.selectbox('Transmission', transmission_df)
    bodyStyle_option = st.selectbox('Body Style', bodyStyle_df)
    reserve_option = st.selectbox('Reserve', reserve_df)
    mileage_option = st.text_input('Mileage')
    vin_option = st.text_input('Vin')
    if st.button('Submit'):
        res = get_vin_info(vin_option)
        mean = res["mean"]
        std = res["stdev"]
        count_over_days = res["count"] / 90
        newres= rq.post(URL, json={"rows": [{"Make": make_option,
                                             "Model": model_option,
                                             "Mileage": float(mileage_option),
                                             "Title Status": title_option,
                                             "Engine": engine_option,
                                             "Drivetrain": drive_option,
                                             "Transmission" : transmission_option,
                                             "Body Style": bodyStyle_option,
                                             "Y_N_Reserve": reserve_option,
                                             "Year": int(year_option),
                                             "Market_Value_Mean": float(mean),
                                             "Market_Value_Std": float(std),
                                             "Count_Over_Days": float(count_over_days),
                                             "Adj Close": float(sp500)}]})
        newres = newres.json()
        newres = newres[0]

        if newres >= float(mean):
            SELLSTRING = "recommended"
        else:
            SELLSTRING = 'not recommended'
        st.write(f"Predicted Price on CarsAndBids.com: ${round(newres)}")
        st.write(f"It is {SELLSTRING} that you sell your car on CarsAndBids.com")

with model:
    st.header('Model Loss')

with chart:
    with open('pickled_models/version8-12.pkl', "rb") as f:
        graph = pickle.load(f)
        y = (graph[1].train_score_ / max(graph[1].train_score_ ))
        x = range(0, graph[1].train_score_.shape[0])
        plt = px.scatter(x=x, y=y, labels=dict(x="N_estimators", y="Loss (%)"))
        st.plotly_chart(plt)
