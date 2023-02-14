"""Spins up the Flask server for model predictions

Requires the calling environment to have installed:
- Pandas
- Pickle
- Flask

This server contains the following endpoints:
  /predict (POST) - returns the column headers of the file
"""
import json
import pandas as pd
from sqlalchemy import create_engine
from flask import Flask, request, jsonify
import pandas as pd
import boto3
import pickle as pkl
import os
import shap

session = boto3.Session(
    aws_access_key_id = os.environ["ACCESS_KEY"],
    aws_secret_access_key=os.environ["ACCESS_SECRET"],
    region_name = os.environ["REGION"]
)

s3 = session.resource('s3')
URI = os.environ["URI"]

engine = create_engine(URI)

# scores = pd.read_sql_table('models_score', con=engine)
# max_score = scores['test_score'].astype(float).idxmax()
# name = scores["path"][max_score]

mod_api = pkl.loads(s3.Bucket("carsalesmodel").Object('thismod.pkl').get()['Body'].read())



app = Flask(__name__)

@app.route('/')


@app.route("/predict", methods=['POST'])
def predict():
    """Receives car metadata, feeds into trained model, returns prediction as JSON
    Receives data (JSON) in the following structure:
    key : value
    Returns
    ----------
    preds
        estimated sale value on CarsAndBids.com and the standard deviation
    """
    data = request.get_data()
    data = data.decode('UTF-8')
    data = json.loads(data)
    data = pd.DataFrame(data["rows"], index = [*range(len(data["rows"]))])    
    preds = mod_api.predict(data)
    return jsonify(list(preds))



@app.route("/predict_streamlit", methods=['POST'])
def predict_streamlit():
    """Receives car metadata, feeds into trained model, returns prediction as JSON
    Receives data (JSON) in the following structure:
    key : value
    Returns
    ----------
    preds
        estimated sale value on CarsAndBids.com and the standard deviation
    """
    data = request.get_data()
    data = data.decode('UTF-8')
    data = json.loads(data)
    data = data['rows'][0]
    model_name = data['tree_model']
    del data['tree_model']
    data = pd.DataFrame(data, index = [0])
    mod = pkl.loads(s3.Bucket("carsalesmodel").Object(f'{model_name}').get()['Body'].read())
    shap_data = mod['columntransformer'].fit_transform(data)
    exp = shap.TreeExplainer(mod['gradientboostingregressor'], shap_data)
    exp =  exp.shap_values(shap_data)
    print(exp)
    preds = mod.predict(data)
    return jsonify(list(preds, exp))

if __name__ == '__main__':
    app.run()
