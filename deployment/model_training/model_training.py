from sqlalchemy import create_engine, text
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split, GridSearchCV
from category_encoders import TargetEncoder
from datetime import date
from pull_yfinance import pull_yfin
import pickle as pkl
import os
import boto3
import shap
import argparse
import numpy as np
import pandas as pd

session = boto3.Session(
    aws_access_key_id      = os.environ["ACCESS_KEY"],
    aws_secret_access_key  = os.environ["ACCESS_SECRET"],
    region_name            = os.environ["REGION"])

def main(with_or_without_market):
  today = date.today().strftime("%m-%d-%Y")
  training_rounds = int(os.environ['TRAINING_ROUNDS'])
  uri             = os.environ["URI"]
  model_env       = with_or_without_market
  
  engine = create_engine(uri)
  with engine.connect() as conn:
      get_idx = text('''SELECT "id" FROM "models_score"''')
      idx     = conn.execute(get_idx).fetchall()
  
  if idx == []:
    id_max = 0
  else:
    id_max = max([id_ for (id_, ) in idx])
    
  if with_or_without_market == 'with_market':
        sqltxt   = '''SELECT * FROM "cars_bids_listings"
                      INNER JOIN "vin_audit_data"
                      ON "cars_bids_listings"."vin" = "vin_audit_data"."vin"'''
        
        cols     =  ["make", "drivetrain", "model", "mileage", "year", "price",
                     "body_style",  "y_n_reserve", 'market_value_mean',
                     'market_value_std', 'count_over_days', 'Adj Close', 
                     'engine', 'title_status', 'transmission']
        
        num_cols =  ["mileage", "year", 'market_value_mean', 
                     'market_value_std', 'count_over_days', 
                     'Adj Close']
        
  else:
        sqltxt   = '''SELECT * FROM "cars_bids_listings"'''
        
        cols     = ["make", "drivetrain", "model", "mileage", "year", "price",
                    "body_style", 'engine', 'title_status', 'transmission',  "y_n_reserve"]
       
        num_cols = ["mileage", "year"]

  
  full_data = pd.read_sql_query(text(sqltxt), con=engine)
  full_data.drop_duplicates(inplace=True, subset=['vin'])
  full_data.reset_index(inplace=True)

  if with_or_without_market == 'with_market':
    full_data = pull_yfin(full_data)
    
  prelim_data = full_data[cols]
  prelim_data = prelim_data.applymap(lambda x: None if x == 'None' else x)
  prelim_data.dropna(inplace=True, how='any')
  prelim_data.reset_index(inplace=True)

  # convert these to numeric and change capitalization
  for i in num_cols:
    prelim_data[i] = prelim_data[i].astype(float)
    
  cat_cols = ["make",  "y_n_reserve", "body_style", 
              "drivetrain", "title_status", "transmission"]
  
  target_cols = ["model", "engine"]
  
  scaler = StandardScaler()
  onehot = OneHotEncoder(handle_unknown="ignore")
  target = TargetEncoder(handle_unknown="value")

  num_transformer    = make_pipeline(scaler)
  onehot_transformer = make_pipeline(onehot)
  target_transformer = make_pipeline(target)

  preprocessor = ColumnTransformer(
      transformers=[  ('num',    num_transformer,    num_cols),
                      ('cat',    onehot_transformer, cat_cols),
                      ('target', target_transformer, target_cols)], remainder = "passthrough")

  y              = prelim_data["price"].astype(float)
  X              = prelim_data
  X.drop(columns = ["price"], inplace=True)

  X_tr, X_tst, y_tr, y_tst = train_test_split(X, y, train_size= .8)
  
  mod_name = 'gradientboostingregressor'
  learning_rates = np.random.rand(training_rounds)
  max_depth      = np.random.randint(3, 10, training_rounds)
  n_estimators   = np.random.randint(100, 5000, training_rounds)
  search_grid    = [{mod_name+"__learning_rate":  learning_rates,
                     mod_name+"__max_depth":  max_depth,
                     mod_name+"__n_estimators":  n_estimators}]
  
  pipe = make_pipeline(preprocessor, GradientBoostingRegressor())
  pipe = GridSearchCV(estimator = pipe, param_grid = search_grid, cv = 5, scoring = 'neg_root_mean_squared_error')
  pipe.fit(X_tr, y_tr)
  
  with engine.connect() as conn:
      sqlstmt_ms = text('''INSERT INTO models_score
                          VALUES (:v0, :v1, :v2, :v3)''')
      conn.execute(sqlstmt_ms, v0=id_max+1, v1=str(today), v2=pipe.score(X_tst, y_tst) * -1, v3=model_env)
  
  best_estimator = pipe.best_estimator_
  transformer = best_estimator['columntransformer']
  shap_test_data = transformer.transform(X_tr).toarray()
  exp            = shap.TreeExplainer(best_estimator['gradientboostingregressor'], shap_test_data)

  bucket      = 'collectorcarsalesmodel'
  shap_bucket = 'car-shap-explainers'
  key         = f'{today}_{with_or_without_market}.pkl'
  
  with open(f'/tmp/{key}', 'wb') as f:
    pkl.dump(pipe, f)
  with open(f'/tmp/shap_{key}', 'wb') as g:
    pkl.dump(exp, g)

  s3 = session.resource('s3')
  s3.meta.client.upload_file(Filename=f'/tmp/{key}', Bucket=bucket, Key=key)
  s3.meta.client.upload_file(Filename=f'/tmp/shap_{key}', Bucket=shap_bucket, Key=key)
  return "finished"

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--model_type', type=str, help='Train model with or without market data. options are "with_market" or "without_market"')
  args = parser.parse_args()
  main(args.model_type)
  
