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
import requests as rq

session = boto3.Session(
    aws_access_key_id = os.environ["ACCESS_KEY"],
    aws_secret_access_key=os.environ["ACCESS_SECRET"],
    region_name = os.environ["REGION"]
)

URI = os.environ["URI"]

engine = create_engine(URI)

# scores = pd.read_sql_table('models_score', con=engine)
# max_score = scores['test_score'].astype(float).idxmax()
# name = scores["path"][max_score]



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
    data = data['rows'][0]
    model_name = data['tree_model']
    del data['tree_model']
    data = pd.DataFrame(data, index = [0])
    s3 = session.resource('s3')
    mod = pkl.loads(s3.Bucket("carsalesmodel").Object(f'{model_name}').get()['Body'].read())
    preds = mod.predict(data)
    return jsonify(list(preds))

if __name__ == '__main__':
    app.run()



@app.route("/predict_streamlit", methods=['POST'])
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
    data = data['rows'][0]
    model_name = data['tree_model']
    del data['tree_model']
    data = pd.DataFrame(data, index = [0])
    s3 = session.resource('s3')
    mod = pkl.loads(s3.Bucket("carsalesmodel").Object(f'{model_name}').get()['Body'].read())
    preds = mod.predict(data)
    return jsonify(list(preds))

if __name__ == '__main__':
    app.run()
