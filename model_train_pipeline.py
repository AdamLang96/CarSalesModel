import datetime as dt
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

run_script = True
training_rounds = 1

uri = "postgresql://codesmith:TensorFlow01?@cardata.ceq8tkxrvrbb.us-west-2.rds.amazonaws.com:5432/postgres"
engine = create_engine(uri)
with engine.connect() as conn:
    get_idx = '''SELECT id_ FROM models_score'''
    idx = conn.execute(get_idx).fetchall()

id_max = max([id_ for (id_, ) in idx])

sqlstmt_cb = '''SELECT * FROM "CarsBidData"
              INNER JOIN "VinAuditData"
              ON "CarsBidData"."VIN" = "VinAuditData"."VIN"'''

full_data = pd.read_sql_query(sqlstmt_cb, con=engine)
print(full_data)
# full_data.drop(columns =["index", 'Unnamed: 0', "VIN", "Count", "URL"], inplace=True)

if True:
    prelim_data = full_data[["Make", "Drivetrain", "Model", "Mileage", "Year", "Price", "Sold Type", "Body Style", "Num Bids", "Y_N_Reserve", 'Market_Value_Mean', 'Market_Value_Std', 'Count_Over_Days']]
    num_cols = ["Mileage", "Year", "Num Bids", 'Market_Value_Mean', 'Market_Value_Std', 'Count_Over_Days']

    cat_cols = ["Make", "Sold Type", "Y_N_Reserve", "Body Style", "Drivetrain"]

    target_cols = ["Model"]

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
    
    prelim_data.dropna(inplace=True)
    y = prelim_data["Price"]
    X = prelim_data
    X.drop("Price", axis=1, inplace=True)

    X_tr, X_tst, y_tr, y_tst = train_test_split(X, y, train_size= .8)
    X_tr, X_val, y_tr, y_val = train_test_split(X_tr, y_tr, test_size=.25)
    
    
    if run_script:
        learning_rates = np.random.rand(training_rounds, 1)
        max_depth      = np.random.randint(3, 10, training_rounds)
        n_estimators   = np.random.uniform(100, 5000, training_rounds)
        scoring_data = []
        for i in range(training_rounds):
            model = GradientBoostingRegressor(learning_rate=learning_rates[i], max_depth=int(max_depth[i]), n_estimators=int(n_estimators[i]))
            pipe = make_pipeline(preprocessor, model)
            pipe.fit(X_tr, y_tr)
            val_score = pipe.score(X_val, y_val)
            print(f'{val_score}  :val score')
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
        print(test_score)
        filepath = f"pickled_models/{str(dt.date.today())}_model.pkl"
        new_id = id_max + 1

        with engine.connect() as conn:
            sqlstmt_ms = text('''INSERT INTO models_score
                              VALUES (:v0, :v1, :v2)''')
            conn.execute(sqlstmt_ms, v0=new_id, v1=filepath, v2=test_score)

        with open(filepath, "wb") as f:
            pkl.dump(pipe, f)