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
import os
import boto3
from streamlit_option_menu import option_menu
# from vin_api import get_vin_info

session = boto3.Session(
    aws_access_key_id = "AKIAUH63BSS4PNGLHLFR",
    aws_secret_access_key="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",
    region_name = 'us-west-2'
)


name = 'thismod'
s3 = session.resource('s3')
mod = pickle.loads(s3.Bucket("carsalesmodel").Object(f'{name}.pkl').get()['Body'].read())

# URI = os.environ["URI"]

engine = create_engine('postgresql+psycopg2://postgres:postgres@classical-project.ceq8tkxrvrbb.us-west-2.rds.amazonaws.com/postgres')

URL = 'http://127.0.0.1:8080/predict'

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
st.set_page_config(layout="wide", page_title="Car Sale Value")
headercol1, headercol2 = st.columns(2)
with st.container():
    with headercol1:
        st.markdown("<h1 style='text-align: center; color: black;'>How Much is Your Collector Car Worth?</h1>", unsafe_allow_html=True)
        st.text('''Commodo nulla facilisi nullam vehicula. Risus feugiat in ante metus dictum at tempor commodo ullamcorper.\nBlandit cursus risus at ultrices.\nTurpis in eu mi bibendum neque.\nEu mi bibendum neque egestas congue quisque egestas diam. Fermentum leo vel orci porta non pulvinar.Porttitor rhoncus dolor purus non enim praesent elementum\nQuam lacus suspendisse faucibus interdum posuere lorem.\nDonec massa sapien faucibus et molestie ac feugiat sed lectus. Consequat ac felis donec et odio pellentesque diam volutpat. Mauris cursus mattis molestie a iaculis at erat.\nQuam vulputate dignissim suspendisse in est ante in nibh. Sed enim ut sem viverra.''')
    with headercol2:
        st.image('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTe1SBdlXWtJ96-zcUnN05YMaumzpJ-q2ei-A&usqp=CAU', width=500)
selected_navbar = option_menu(None, ["Home", "Predict", "FAQ", 'About', 'Model', 'API'], orientation="horizontal")

    
col1, col2, col3, col4 = st.columns(4)
dataset = st.container()
model = st.container()
years = range(1980, 2023)
chart = st.container()

if selected_navbar == "Home":
    st.text('''             Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Amet consectetur adipiscing elit duis tristique sollicitudin nibh. Nulla facilisi cras fermentum odio eu. 
                Imperdiet dui accumsan sit amet. Nullam non nisi est sit amet facilisis. 
                Nulla facilisi nullam vehicula ipsum a arcu cursus vitae congue. Praesent elementum facilisis leo vel fringilla. Quis hendrerit dolor magna eget est lorem ipsum. Sollicitudin nibh sit amet commodo nulla facilisi. 
                Cursus risus at ultrices mi. Adipiscing vitae proin sagittis nisl rhoncus mattis rhoncus urna neque. Eros donec ac odio tempor. 
                Urna condimentum mattis pellentesque id nibh tortor id. Adipiscing vitae proin sagittis nisl rhoncus mattis rhoncus urna neque. Molestie at elementum eu facilisis sed odio morbi quis. Eleifend mi in nulla posuere sollicitudin aliquam ultrices sagittis orci. Placerat orci nulla pellentesque dignissim.
            
            Sed ullamcorper morbi tincidunt ornare. Eget aliquet nibh praesent tristique magna. 
                Sem viverra aliquet eget sit amet. Sodales neque sodales ut etiam sit amet nisl. 
                Lobortis mattis aliquam faucibus purus in massa. Pharetra magna ac placerat vestibulum lectus mauris ultrices. 
                Commodo nulla facilisi nullam vehicula. Risus feugiat in ante metus dictum at tempor commodo ullamcorper. 
                Blandit cursus risus at ultrices. Turpis in eu mi bibendum neque. Eu mi bibendum neque egestas congue quisque egestas diam. 
                Fermentum leo vel orci porta non pulvinar. Porttitor rhoncus dolor purus non enim praesent elementum. Quam lacus suspendisse faucibus interdum posuere lorem. 
                Donec massa sapien faucibus et molestie ac feugiat sed lectus. Consequat ac felis donec et odio pellentesque diam volutpat. Mauris cursus mattis molestie a iaculis at erat. Quam vulputate dignissim suspendisse in est ante in nibh. Sed enim ut sem viverra.
            
            Enim blandit volutpat maecenas volutpat blandit aliquam etiam erat. 
                Turpis egestas maecenas pharetra convallis posuere. 
                Nibh nisl condimentum id venenatis. Eget nunc scelerisque viverra mauris in. 
                Quis eleifend quam adipiscing vitae proin sagittis nisl. 
                Sit amet venenatis urna cursus eget nunc scelerisque viverra. 
                Risus in hendrerit gravida rutrum. Enim neque volutpat ac tincidunt vitae semper quis lectus nulla. 
                Aliquet lectus proin nibh nisl condimentum. Fames ac turpis egestas maecenas pharetra convallis posuere. 
                Gravida cum sociis natoque penatibus et magnis dis parturient montes. 
                Volutpat sed cras ornare arcu dui vivamus.
            
            Eu volutpat odio facilisis mauris sit amet massa. 
                Ipsum dolor sit amet consectetur adipiscing elit pellentesque habitant morbi. 
                Eleifend donec pretium vulputate sapien. Malesuada bibendum arcu vitae elementum curabitur vitae nunc sed.
            
            Convallis aenean et tortor at risus. Et ultrices neque ornare aenean euismod. 
                Eu ultrices vitae auctor eu augue ut lectus. Gravida arcu ac tortor dignissim convallis aenean et tortor at. 
                Mattis enim ut tellus elementum sagittis vitae et. Amet mauris commodo quis imperdiet. Dolor purus non enim praesent elementum.
                Maecenas accumsan lacus vel facilisis volutpat est. Sit amet mauris commodo quis imperdiet. Ornare massa eget egestas purus. 
                Sit amet luctus venenatis lectus magna fringilla urna. Tristique senectus et netus et malesuada fames ac turpis. 
                Tempor orci dapibus ultrices in iaculis nunc sed augue. Urna porttitor rhoncus dolor purus non enim praesent. 
                Aliquet nec ullamcorper sit amet risus nullam eget felis.
            
            Orci eu lobortis elementum nibh tellus. Quis lectus nulla at volutpat diam ut venenatis tellus in. 
                Morbi quis commodo odio aenean sed adipiscing diam donec adipiscing. Et egestas quis ipsum suspendisse. 
                Diam phasellus vestibulum lorem sed risus. Fringilla urna porttitor rhoncus dolor. Diam volutpat commodo sed egestas egestas fringilla phasellus. 
                Scelerisque in dictum non consectetur. In arcu cursus euismod quis viverra nibh cras pulvinar mattis. 
                Velit dignissim sodales ut eu. Ac auctor augue mauris augue neque gravida. Cursus vitae congue mauris rhoncus. 
                A scelerisque purus semper eget duis at tellus.''')
                
if selected_navbar == "FAQ":
    with st.container():
        with st.expander("Question One"):
            st.write('answer one')
        with st.expander("Question Two"):
            st.write('answer two')
        with st.expander("Question Three"):
            st.write('answer three')
        with st.expander("Question Three"):
            st.write('answer three')
        with st.expander("Question Four"):
            st.write('answer three')

if selected_navbar == "Predict":
    sp500 = 4147
    with dataset:
        with st.container():
                with col1:
                    make_option = st.selectbox('Make', make_df)
                    model_option = st.selectbox('Model', model_df)
                    year_option = st.selectbox("Year", years)
                with col2:
                    engine_option = st.selectbox('Engine', engine_df)
                    title_option = st.selectbox('Title', title_status_df)
                    drive_option = st.selectbox('Drive', drive_train_df)
                with col3:
                    bodyStyle_option = st.selectbox('Body Style', bodyStyle_df)
                    reserve_option = st.selectbox('Reserve', reserve_df)
                    transmission_option = st.selectbox('Transmission', transmission_df)
                with col4:
                    vin_option = st.text_input('Vin')
                    mileage_option = st.text_input('Mileage')
                button = st.button("Submit", use_container_width=True)
        
        if button:
            mean = '5000'
            std = '120'
            count_over_days = '12'
            newres= rq.post(URL, json={"rows": [{   "make": make_option,
                                                    "model": model_option,
                                                    "mileage": mileage_option,
                                                    "status": title_option , 
                                                    "engine":engine_option,
                                                    "drivetrain": drive_option,
                                                    "transmission" :transmission_option,
                                                    "bodystyle": bodyStyle_option,
                                                    "y_n_reserve":reserve_option,
                                                    "year":year_option,
                                                    'market_value_mean': "20000", 
                                                    'market_value_std':'400', 
                                                    'count_over_days':"10", 
                                                    'Adj Close':'4000'}]})
            rq.get('http://marketvalue.vinaudit.com/getmarketvalue.php?key=VA_DEMO_KEY&vin=JM1NA3533S0611425&format=json&period=90&mileage=average')
            # print(vin)
            print('complete')
            newres = newres.json()
            newres = newres[0]
            mean = 50
            if newres >= float(mean):
                SELLSTRING = "recommended"
            else:
                SELLSTRING = 'not recommended'
            st.write(f"Predicted Price on CarsAndBids.com: ${round(newres)}")
            st.write(f"It is {SELLSTRING} that you sell your car on CarsAndBids.com")

api_column1, api_column2, api_column3 = st.columns(3)          
if selected_navbar == "API":
        st.title("Our API is free to use and available at URL/predict")
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
         

if selected_navbar == "Model":
        with model:
            st.header('Training Loss')
        with chart:
                graph = mod
                y = (graph[1].train_score_ / max(graph[1].train_score_ ))
                x = range(0, graph[1].train_score_.shape[0])
                plt = px.scatter(x=x, y=y, labels=dict(x="N_estimators", y="Loss (%)"))
                st.plotly_chart(plt)

st.write("Developed by Adam Lang and David Kim [Github Repo]('https://github.com/CodeSmithDSMLProjects/CarSalesModel')")
