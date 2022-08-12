from sqlite3 import connect
from turtle import title
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, VARCHAR, Numeric
from sqlalchemy import Table, text
from sqlalchemy.ext.declarative import declarative_base
import requests as rq
from vin_api import getVinInfo
import yfinance as yf
import datetime
uri = "postgresql://codesmith:TensorFlow01?@cardata.ceq8tkxrvrbb.us-west-2.rds.amazonaws.com:5432/postgres"
engine = create_engine(uri)

url = 'http://ec2-54-185-209-122.us-west-2.compute.amazonaws.com:8080/predict'
x = rq.post(url, json={"rows": [{"Make": "Porsche","Model": "Cayenne","Mileage": "167500.0","Title Status": "Clean" , "Location": "2996", "Engine":"3.6L V6","Drivetrain": "4WD/AWD","Transmission" :"Manual (6-Speed)","Body Style":" SUV/Crossover","Exterior Color": "Black","Interior Color" :"Black", "Sold Type" : "Sold For","Num Bids" :"16.0","Y_N_Reserve":" No Reserve","Year":"2012.0","Market_Value_Mean":"22312.47","Market_Value_Std": "3907","Count_Over_Days": "0.884393063583815","Adj Close": "4509.3701171875"}, {"Make": "Porsche","Model": "Cayenne","Mileage": "167500.0","Title Status": "Clean" , "Location": "2996", "Engine":"3.6L V6","Drivetrain": "4WD/AWD","Transmission" :"Manual (6-Speed)","Body Style":" SUV/Crossover","Exterior Color": "Black","Interior Color" :"Black", "Sold Type" : "Sold For","Num Bids" :"16.0","Y_N_Reserve":" No Reserve","Year":"2012.0","Market_Value_Mean":"22312.47","Market_Value_Std": "3907","Count_Over_Days": "0.884393063583815","Adj Close": "4509.3701171875"}]})

sp500 = yf.download("^GSPC", start= '2019-1-1', end= str(datetime.date.today()))
sp500 = sp500["Adj Close"].iat[-1]

# def connection_to_data(engine) -> pd.DataFrame:
model_sql_query = 'SELECT DISTINCT "Model" FROM "CarsBidData";' # , "Make", "Exterior Color" 
make_sql_query = 'SELECT DISTINCT "Make" FROM "CarsBidData";'
exterior_color_sql_query = 'SELECT DISTINCT "Exterior Color" FROM "CarsBidData";'
interior_color_sql_query = 'SELECT DISTINCT "Interior Color" FROM "CarsBidData";'
engine_sql_query = 'SELECT DISTINCT "Engine" FROM "CarsBidData";'
title_status_sql_query = 'SELECT DISTINCT "Title Status" FROM "CarsBidData";'
drive_train_sql_query = 'SELECT DISTINCT "Drivetrain" FROM "CarsBidData";'
transmission_sql_query = 'SELECT DISTINCT "Transmission" FROM "CarsBidData";'
bodyStyle_sql_query = 'SELECT DISTINCT "Body Style" FROM "CarsBidData";'
soldType_sql_query = 'SELECT DISTINCT "Sold Type" FROM "CarsBidData";'
ynReserve_sql_query = 'SELECT DISTINCT "Y_N_Reserve" FROM "CarsBidData";'
location_sql_query = 'SELECT DISTINCT "Location" FROM "CarsBidData";'
vin_sql_query = 'SELECT "VIN" FROM "CarsBidData" LIMIT 1;'


with engine.connect() as connection:
    make_df = pd.read_sql_query(make_sql_query, con = connection)
    model_df = pd.read_sql_query(model_sql_query, con = connection)
    exterior_color_df = pd.read_sql_query(exterior_color_sql_query, con = connection)
    interior_color_df = pd.read_sql_query(interior_color_sql_query, con = connection)
    engine_df = pd.read_sql_query(engine_sql_query, con = connection)
    title_status_df = pd.read_sql_query(title_status_sql_query, con = connection)
    drive_train_df = pd.read_sql_query(drive_train_sql_query, con = connection)
    transmission_df = pd.read_sql_query(transmission_sql_query, con = connection)
    bodyStyle_df = pd.read_sql_query(bodyStyle_sql_query, con=connection)
    soldType_df = pd.read_sql_query(soldType_sql_query, con = connection)
    reserve_df = pd.read_sql_query(ynReserve_sql_query, con = connection)
    location_df = pd.read_sql_query(location_sql_query, con = connection)
    vin = pd.read_sql_query(vin_sql_query, con = connection)

# print(connection_to_data(engine))

header = st.container()
dataset = st.container()
model = st.container()
years = range(1980, 2023)

with header:
    st.title('Car Sales Model')

with dataset:
    st.header('Cars Model Dataset')

    display = st.columns(1)   

    make_option = st.selectbox('MAKER', make_df)
    model_option = st.selectbox('Model', model_df)
    year_option = st.selectbox("Year", years)
    exterior_color_option = st.selectbox('Exterior Color', exterior_color_df)
    interior_color_option = st.selectbox('Interior Color', interior_color_df)
    engine_option = st.selectbox('Engine', engine_df)
    title_option = st.selectbox('Title', title_status_df)
    drive_option = st.selectbox('Drive', drive_train_df)
    transmission_option = st.selectbox('Transmission', transmission_df)
    bodyStyle_option = st.selectbox('Body Style', bodyStyle_df)
    soldType_option = st.selectbox('Sold Type', soldType_df)
    reserve_option = st.selectbox('Reserve', reserve_df)
    
    location_option = st.selectbox('Location', location_df)

    mileage_option = st.text_input('Mileage')

    vin_option = st.text_input('Vin')
    num_bids = st.text_input('NumBids')
    if st.button('Submit'):
        res = getVinInfo(vin_option)
        mean = res["mean"]
        std = res["stdev"]
        count_over_days = res["count"] / 90
        
        newres= rq.post(url, json={"rows": [{"Make": make_option,"Model": model_option,"Mileage": float(mileage_option),
                                     "Title Status": title_option , "Location": int(location_option), "Engine": engine_option,
                                     "Drivetrain": drive_option,"Transmission" : transmission_option,"Body Style": bodyStyle_option,
                                     "Exterior Color": exterior_color_option,"Interior Color" : interior_color_option, "Sold Type" : soldType_option,"Num Bids" : num_bids,
                                     "Y_N_Reserve": reserve_option,"Year": int(year_option),"Market_Value_Mean": float(mean),"Market_Value_Std": float(std),
                                     "Count_Over_Days": float(count_over_days),"Adj Close": float(sp500)}]})
                
        
        st.write(newres.json())
    


# user input vin number return market value mean, market value std, 
# take row of csv, and make request to server

with model:
    st.header('Model Score')



    


    
                 