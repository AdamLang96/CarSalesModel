"""Spins up the Flask server for model predictions

Requires the calling environment to have installed:
- Pandas
- Pickle
- Flask

This server contains the following endpoints:
  /predict (POST) - returns the column headers of the file
"""
import json
import pickle as pkl
import pandas as pd
from sqlalchemy import create_engine
from flask import Flask, request, jsonify
import pandas as pd
import boto3
import pickle as pkl

URI = """postgresql://codesmith:TensorFlow01?@cardata.ceq8tkxrvrbb.us-west-2.rds.amazonaws.com:5432/postgres"""
engine = create_engine(URI)

scores = pd.read_sql_table('models_score', con=engine)
max_score = scores['score'].idxmax()
name = scores['path'][max_score]
print(name)
# bucket='your_bucket_name'
# key='your_pickle_filename.pkl'
# pickle_byte_obj = pickle.dumps([var1, var2, ..., varn]) 
# s3_resource = boto3.resource('s3')
# s3_resource.Object(bucket,key).put(Body=pickle_byte_obj)

s3 = boto3.resource('s3')
mod = pkl.loads(s3.Bucket("carsalesmodel").Object(f'{name}.pkl').get()['Body'].read())
# s3_client = boto3.client('s3')
# s3_response_object = s3_client.get_object(Bucket='carsalesmodel', Key=name)# load from S3 the pickle-serialized pipeline object
# mod = s3_response_object['Body'].read() # may have to un-pickle
# mod = pkl.loads(mod)
# print(object_content)
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
    preds = mod.predict(data)
    return jsonify(list(preds))

if __name__ == '__main__':
    app.run()
