from sqlalchemy import create_engine
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from category_encoders import TargetEncoder
import pickle as pkl
from sqlalchemy import text
import yfinance as yf
import os
import boto3
from datetime import date
from uuid import uuid4
import hashlib

session = boto3.Session(
    aws_access_key_id = "AKIAUH63BSS4PNGLHLFR",
    aws_secret_access_key="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",
    region_name = 'us-west-2'
)


def main():
  today = date.today()
  today = today.strftime("%m-%d-%Y")
  today = str(today) + str(uuid4())

  training_rounds = 1
  uri = "postgresql+psycopg2://codesmith:TensorFlow01?@database-1.ceq8tkxrvrbb.us-west-2.rds.amazonaws.com/postgres"
  model_env = "test"
  

  engine = create_engine(uri)
  with engine.connect() as conn:
      get_idx = text('''SELECT "id" FROM "models_score"''')
      idx = conn.execute(get_idx).fetchall()
      print(f'idx: {idx}')
      
  if idx == []:
    id_max = 0
  else:
    id_max = max([id_ for (id_, ) in idx])
    print(id_max)


  sqlstmt_cb = text('''SELECT * FROM "cars_bids_listings"
                INNER JOIN "vin_newest_final"
                ON "cars_bids_listings"."vin" = "vin_audit_data"."vin"''')

  full_data = pd.read_sql_query(sqlstmt_cb, con=engine)
  full_data["Date"] = pd.to_datetime(full_data["date"])
  full_data.drop(columns="date")
  sp500 = yf.download("^GSPC", start= '2019-1-1', end=str(date.today())) 
  idx = pd.date_range('2019-1-1', str(date.today()))
  sp500 = sp500.reindex(idx, fill_value=0)

  price_mem = -1
  vol_mem = -1
  first_ind = 0
  for i in range(len(sp500['Adj Close'])):
    if sp500['Adj Close'][i] == 0:
      if i == 0:
        if sp500['Open'][i+1] == 0:
          price_mem = sp500['Open'][i+2]
          vol_mem = sp500['Volume'][i+2]
        else:
          price_mem = sp500['Open'][i+1]
          vol_mem = sp500['Volume'][i+1]
      sp500['Open'][i] = price_mem
      sp500['High'][i] = price_mem
      sp500['Low'][i] = price_mem
      sp500['Close'][i] = price_mem
      sp500['Adj Close'][i] = price_mem
      sp500['Volume'][i] = vol_mem
    else:
      vol_mem = sp500['Volume'][i]
      price_mem = sp500['Adj Close'][i]
  full_data.drop_duplicates(inplace=True, subset=['vin'])
  sp500 = pd.DataFrame(sp500)
  sp500 = sp500.groupby(sp500.index).first()
  full_data.reset_index()
  full_data = full_data.merge(sp500, left_on="Date", right_index=True, how="left")
  prelim_data = full_data[["make", "drivetrain", "model", "mileage", "year", "price",
                              "bodystyle",  "y_n_reserve", 'market_value_mean',
                              'market_value_std', 'count_over_days', 'Adj Close', 'engine', 'status', 'transmission']]

  prelim_data.dropna(inplace=True, axis=0)

  # convert these to numeric and change capitalization
  num_cols = ["mileage", "year", 'market_value_mean', 'market_value_std', 'count_over_days', 'Adj Close']
  for i in num_cols:
    prelim_data[i] = prelim_data[i].astype(float)
  cat_cols = ["make",  "y_n_reserve", "bodystyle", "drivetrain", "status","transmission"]
  target_cols = ["model", "engine"]
  scaler = StandardScaler()
  onehot = OneHotEncoder(handle_unknown="ignore")
  target = TargetEncoder(handle_unknown="value")

  num_transformer    = make_pipeline(scaler)
  onehot_transformer = make_pipeline(onehot)
  target_transformer = make_pipeline(target)

  preprocessor = ColumnTransformer(
      transformers=[('num', num_transformer, num_cols),
                      ('cat', onehot_transformer, cat_cols),
                      ('target', target_transformer, target_cols)], remainder="passthrough")


  y = prelim_data["price"].astype(float)
  X = prelim_data
  X.drop(columns=["price"], inplace=True)

  X_tr, X_tst, y_tr, y_tst = train_test_split(X, y, train_size= .8)
  X_tr, X_val, y_tr, y_val = train_test_split(X_tr, y_tr, test_size=.25)

  learning_rates = np.random.rand(training_rounds, 1)
  max_depth      = np.random.randint(3, 10, training_rounds)
  n_estimators   = np.random.uniform(100, 5000, training_rounds)
  scoring_data = []
  for i in range(training_rounds):
      model = GradientBoostingRegressor(learning_rate=learning_rates[i], max_depth=int(max_depth[i]), n_estimators=int(n_estimators[i]))
      pipe = make_pipeline(preprocessor, model)
      pipe.fit(X_tr, y_tr)
      val_score = pipe.score(X_val, y_val)
      val_score = {"learning_rate":round(learning_rates[i][0], 3), "max_depth":int(max_depth[i]), "n_estimators":int(n_estimators[i]), "score": val_score}
      scoring_data.append(val_score)
  scoring_data = pd.DataFrame(scoring_data)
  max_score_idx = scoring_data["score"].idxmax()
  max_row   = scoring_data.iloc[max_score_idx, :]
  model = GradientBoostingRegressor(learning_rate=max_row[0], max_depth=int(max_row[1]), n_estimators=int(max_row[2]))
  y_tr = np.array(y_tr)
  y_tr = np.reshape(y_tr, (y_tr.shape[0], 1))
  y_val = np.array(y_val)
  y_val = np.reshape(y_val, (y_val.shape[0], 1))
  y_full = np.concatenate((y_tr, y_val), axis=0)
  y_full = y_full.ravel()
  x_full = pd.concat([X_tr, X_tst], axis=0)
  pipe = make_pipeline(preprocessor, model)
  pipe.fit(X_tr, y_tr)
  test_score = pipe.score(X_tst, y_tst)
  new_id = id_max + 1

  with engine.connect() as conn:
      sqlstmt_ms = text('''INSERT INTO models_score
                          VALUES (:v0, :v1, :v2, :v3)''')
      conn.execute(sqlstmt_ms, v0=new_id, v1=str(today), v2=test_score, v3=model_env)

  bucket = 'carsalesmodel'
  key = 'testuploadmod_indocker_again.pkl'
  
  with open(f'/tmp/{key}', 'wb') as f:
    pkl.dump(pipe, f)
  
  hashlib.md5(open(f'/tmp/{key}','rb').read()).hexdigest()
  print(hashlib.md5(open(f'/tmp/{key}','rb').read()).hexdigest())
  with open(f'/tmp/{key}', 'rb') as g:
    s3 = session.resource('s3')
    s3.Object(bucket,key).put(Body=g)
  # mod = pkl.load(g)
  # pkl_obj = pkl.dumps(pipe)
  # s3= boto3.resource('s3')
  # s3.Object(bucket,key).put(Body=mod)
  return "finished"

  # with open("/Users/adamgabriellang/DSML/CarSalesModel/server/thismod.pkl", 'rb') as f:
    
  # s3 = session.resource('s3')
  # s3.meta.client.upload_file(Filename='thismod.pkl', Bucket=bucket, Key=key)
  # return True

  # mod = pkl.load(g)
  # pkl_obj = pkl.dumps(pipe)
  # s3= boto3.resource('s3')
  # s3.Object(bucket,key).put(Body=mod)
  # return "finished"



