from flask import Flask, request, jsonify
import json
import pickle as pkl
import pandas as pd
import os
MODEL_DIR = os.environ["MODEL_DIR"]

with open (str(MODEL_DIR), "rb") as f:
  mod = pkl.load(f)
  f.close()

app = Flask(__name__)

@app.route('/')

@app.route("/predict", methods=['POST'])
def predict():
  data = request.get_data()
  data = data.decode('UTF-8')
  data = json.loads(data)
  data = pd.DataFrame(data["rows"], index = [*range(len(data["rows"]))])
  preds = mod.predict(data)
  return jsonify(list(preds))
  







if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()
