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
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from category_encoders import TargetEncoder
import numpy as np
import shap
import re



def get_column_names_from_ColumnTransformer(column_transformer):
    col_name = []
    for transformer_in_columns in column_transformer.transformers_[:-1]:#the last transformer is ColumnTransformer's 'remainder'
        raw_col_name = transformer_in_columns[2]
        if isinstance(transformer_in_columns[1], Pipeline): 
            transformer = transformer_in_columns[1].steps[-1][1]
        else:
            transformer = transformer_in_columns[1]
        try:
            if isinstance(transformer, TargetEncoder):
                names = list(transformer.get_feature_names(raw_col_name))
            names = transformer.get_feature_names()
        except AttributeError: # if no 'get_feature_names' function, use raw column name
            names = raw_col_name
        if isinstance(names, np.ndarray): # eg.
            col_name += names.tolist()
        elif isinstance(names,list):
            col_name += names    
        elif isinstance(names,str):
            col_name.append(names)
    return col_name




session = boto3.Session(
    aws_access_key_id = os.environ["ACCESS_KEY"],
    aws_secret_access_key=os.environ["ACCESS_SECRET"],
    region_name = os.environ["REGION"]
)

s3 = session.resource('s3')
URI = os.environ["URI"]
engine = create_engine(URI)

scores = pd.read_sql_table('models_score', con=engine)
max_score = scores['test_score'].astype(float).idxmax()
name = scores["path"][max_score]

mod_api = pkl.loads(s3.Bucket("carsalesmodel").Object(f'{name}.pkl').get()['Body'].read())

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
    shap_data = mod['columntransformer']
    featurenames = get_column_names_from_ColumnTransformer(shap_data)
    featurenames.append('model')
    featurenames.append('engine')
    shap_data_prediction = shap_data.transform(data).toarray()
    shap_exp = pkl.loads(s3.Bucket("shap-explainers").Object(f'{model_name}').get()['Body'].read())
    shap_exp =  shap_exp.shap_values(shap_data_prediction)
    shap_exp = shap_exp[0]
    feature_dict = {}
    feature_map = {"Make":'x0', "Reserve":'x1', "Body Style":'x2', "Drivetrain":'x3', "Title": 'x4', "Transmission": 'x5'}
    for i in feature_map:
        name, prefix = i, feature_map[i]
        feature_sum = 0
        for j in range(len(featurenames)):
            if re.search(prefix, featurenames[j]):
                feature_sum += shap_exp[j]
            elif featurenames[j]=='model':
                feature_dict["Model"] = shap_exp[j]
            elif featurenames[j]=='engine':
                feature_dict["Engine"] = shap_exp[j]
            elif featurenames[j]=='year':
                feature_dict["Year"] = shap_exp[j]
            elif featurenames[j]=='mileage':
                feature_dict["Mileage"] = shap_exp[j]
        feature_dict[name] = feature_sum
        feature_sum = 0        
    preds = list(mod.predict(data))
    return jsonify(list([preds, feature_dict]))

if __name__ == '__main__':
    app.run()
