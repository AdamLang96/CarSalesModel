"""Spins up the Flask server for model predictions

Requires the calling environment to have installed:
- Pandas
- Pickle
- Flask

This server contains the following endpoints:
  /predict (POST) - returns the column headers of the file
"""
import os
import json
import pickle as pkl
import pandas as pd

from flask import Flask, request, jsonify

MODEL_DIR = os.environ["MODEL_DIR"]

with open (str(MODEL_DIR), "rb") as f:
    mod = pkl.load(f)
    f.close()

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
