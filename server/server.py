import json
import pandas as pd
from sqlalchemy import create_engine
from flask import Flask, request, jsonify
import pandas as pd
import boto3
import pickle as pkl
import os
from sklearn.model_selection import GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from category_encoders import TargetEncoder
import numpy as np
import shap
import re
import requests as rq
import yfinance as yf
from datetime import date
from functools import lru_cache

def get_column_names_from_ColumnTransformer(column_transformer):
    col_name = []
    for transformer_in_columns in column_transformer.transformers_[:-1]:
        raw_col_name = transformer_in_columns[2]
        if isinstance(transformer_in_columns[1], Pipeline): 
            transformer = transformer_in_columns[1].steps[-1][1]
        else:
            transformer = transformer_in_columns[1]
        try:
            if isinstance(transformer, TargetEncoder):
                names = list(transformer.get_feature_names(raw_col_name))
            names = transformer.get_feature_names()
        except AttributeError: 
            names = raw_col_name
        if isinstance(names, np.ndarray):
            col_name += names.tolist()
        elif isinstance(names,list):
            col_name += names    
        elif isinstance(names,str):
            col_name.append(names)
    return col_name

@lru_cache(maxsize=100)
def get_vin_info(vin, api_key = 'VA_DEMO_KEY', num_days = 90, mileage = 'average'):
    """pulls data from vinaudit api """
    vinaudit_url = f'https://marketvalue.vinaudit.com/getmarketvalue.php?key={api_key}&vin={vin}&format=json&period={num_days}&mileage={mileage}'
    req = rq.get(url = vinaudit_url)
    data = req.json()
    return data
    
@lru_cache(maxsize=100)   
def fetch_market_data(todays_date):
    sp500 = yf.download("^GSPC", start= '2023-2-1', end=str(todays_date)) 
    sp500 = pd.DataFrame(sp500)
    sp500 = sp500["Adj Close"].iloc[0]
    return sp500

session = boto3.Session(
    aws_access_key_id = os.environ["ACCESS_KEY"],
    aws_secret_access_key=os.environ["ACCESS_SECRET"],
    region_name = os.environ["REGION"]
)

s3 = session.resource('s3')
URI = os.environ["URI"]
engine = create_engine(URI)

scores = pd.read_sql_table('models_score', con=engine)
scores_with_market = scores.loc[scores['environment'] == 'with_market']
scores_without_market = scores.loc[scores['environment'] == 'without_market']

max_score_with_market  = scores_with_market['test_score'].astype(float).idxmin()
max_score_without_market  = scores_without_market['test_score'].astype(float).idxmin()
name_with_market = scores["path"][max_score_with_market]
name_without_market = scores["path"][max_score_without_market]

mod_api_with_market = pkl.loads(s3.Bucket("collectorcarsalesmodel").Object(f'{name_with_market}_with_market.pkl').get()['Body'].read()).best_estimator_
mod_api_without_market = pkl.loads(s3.Bucket("collectorcarsalesmodel").Object(f'{name_without_market}_without_market.pkl').get()['Body'].read()).best_estimator_

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({'hello':'world'})

@app.route("/predict", methods=['POST'])
def predict():
    data = request.get_data()
    data = data.decode('UTF-8')
    data = json.loads(data)
    if 'vin' in list(data.keys()):
        todays_date = date.today()
        m_data = fetch_market_data(todays_date)
        vin = data["vin"]
        vin_info = get_vin_info(vin)
        data["market_value_mean"] = vin_info["mean"]
        data["market_value_std"] = vin_info["stdev"]
        data["count_over_days"] = str(float(vin_info['count']) / 90)
        data["Adj Close"] = m_data
        data = pd.DataFrame({k: [v] for k, v in data.items()})
        preds = mod_api_with_market.predict(data)
    else:
        data = pd.DataFrame({k: [v] for k, v in data.items()})
        preds = mod_api_without_market.predict(data)

    return jsonify(list(preds))


@app.route("/predict_streamlit", methods=['POST'])
def predict_streamlit():

    data = request.get_data()
    data = data.decode('UTF-8')
    data = json.loads(data)
    cols = list(data.keys())
    model_name = data['tree_model']
    del data['tree_model']
    data = pd.DataFrame({k: [v] for k, v in data.items()})
    if 'market_value_mean' in cols:
        pipe = pkl.loads(s3.Bucket("collectorcarsalesmodel").Object(f'{model_name}_with_market.pkl').get()['Body'].read()).best_estimator_
        shap_exp = pkl.loads(s3.Bucket("car-shap-explainers").Object(f'{model_name}_with_market.pkl').get()['Body'].read())
    else:
        pipe = pkl.loads(s3.Bucket("collectorcarsalesmodel").Object(f'{model_name}_without_market.pkl').get()['Body'].read()).best_estimator_
        shap_exp = pkl.loads(s3.Bucket("car-shap-explainers").Object(f'{model_name}_without_market.pkl').get()['Body'].read())
    transformer = pipe['columntransformer']
    feature_names = get_column_names_from_ColumnTransformer(transformer)
    feature_names.append('model')
    feature_names.append('engine')
    shap_data_prediction = transformer.transform(data).toarray()
    shap_exp = shap_exp.shap_values(shap_data_prediction)
    shap_exp = shap_exp[0]
    feature_dict = {}
    feature_map = {"Make":'x0', "Reserve":'x1', "Body Style":'x2', "Drivetrain":'x3', "Title": 'x4', "Transmission": 'x5'}
    for i in feature_map:
        name, prefix = i, feature_map[i]
        feature_sum = 0
        for j in range(len(feature_names)):
            if re.search(prefix, feature_names[j]):
                feature_sum += shap_exp[j]
            elif feature_names[j]=='model':
                feature_dict["Model"] = shap_exp[j]
            elif feature_names[j]=='engine':
                feature_dict["Engine"] = shap_exp[j]
            elif feature_names[j]=='year':
                feature_dict["Year"] = shap_exp[j]
            elif feature_names[j]=='mileage':
                feature_dict["Mileage"] = shap_exp[j]
        feature_dict[name] = feature_sum
        feature_sum = 0        
    preds = list(pipe.predict(data))
    return jsonify(list([preds, feature_dict]))

if __name__ == '__main__':
    app.run()
