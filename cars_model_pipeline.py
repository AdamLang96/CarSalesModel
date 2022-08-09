from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import sklearn as sk
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from category_encoders import TargetEncoder



## read cars and bids data
uri = "postgresql://codesmith:TensorFlow01?@cardata.ceq8tkxrvrbb.us-west-2.rds.amazonaws.com:5432/postgres"
engine = create_engine(uri)
cars_bids_data = pd.read_sql_table("CarsBidData", con=engine)

# read vin audit data
vin_audit_data = pd.read_csv("full_vin_audit_data.csv")

#merge tables

full_data = cars_bids_data.merge(vin_audit_data, on="VIN", how="inner")
full_data.dropna(inplace=True)

# print(full_data.shape)

# make_pipeline(OneHotEncoder())

#Model - Sparse <- encode car type, year made, etc. 
#Engine - <-  standardizable metrics like combustion volume and cylinder count, horsepower/kWh, electric (binary)
#Transmission 4WD/AWD,Manual <- Manual/Automatic  RWD, FWD (4wd is both)
#Location - Sparse (target encoding)

#mileage, num bids, number days, price would need to be normalize

prelim_data = full_data[["Make", "Model", "Mileage", "Year", "Price", "Sold Type", "Num Bids", "Y_N_Reserve", 'Num_Days', 'Market_Value_Mean', 'Market_Value_Std', 'Count_Over_Days']]

num_cols = ["Mileage", "Year", "Num Bids", 'Num_Days', 'Market_Value_Mean', 'Market_Value_Std', 'Count_Over_Days']

cat_cols = ["Make", "Sold Type", "Y_N_Reserve"]

target_cols = ["Model"]

scaler = StandardScaler()
onehot = OneHotEncoder(handle_unknown="ignore")
target = TargetEncoder(handle_unknown="value")

num_transformer = make_pipeline(scaler)
onehot_transformer = make_pipeline(onehot)
target_transformer = make_pipeline(target)

preprocessor = ColumnTransformer(
      transformers=[('num', num_transformer, num_cols),
                    ('cat', onehot_transformer, cat_cols),
                    ('target', target_transformer, target_cols)], remainder="passthrough")


model = GradientBoostingRegressor()
pipe = make_pipeline(preprocessor, model)





# print(prelim_data.dtypes)

ohe = OneHotEncoder(sparse=True)
label_encoder = LabelEncoder()

make_column_encoder = ohe.fit_transform(prelim_data[['Make']])

# target encode make column

# binary encode below two columns
sold_type_onehot = ohe.fit_transform(np.array(prelim_data['Sold Type']).reshape(-1,1)).toarray()
sold_type_onehot = np.transpose(sold_type_onehot)[0]
# print(sold_type_column_encoder.shape)

reserve_onehot = ohe.fit_transform(np.array(prelim_data['Y_N_Reserve']).reshape(-1,1)).toarray()
reserve_onehot = np.transpose(reserve_onehot)[0]
# print(reserve_column_encoder.shape)

mileage_arr = np.array(prelim_data['Mileage'])
num_bids_arr = np.array(prelim_data['Num Bids'])
days_arr = np.array(prelim_data['Num_Days'])
price_arr = np.array(prelim_data['Price'])
market_value_mean_arr = np.array(prelim_data['Market_Value_Mean'])
market_value_std_arr = np.array(prelim_data['Market_Value_Std'])
count_days_arr = np.array(prelim_data['Count_Over_Days'])


standardized_mileage = preprocessing.scale(mileage_arr)
standardized_bids = preprocessing.scale(num_bids_arr)
standardized_days = preprocessing.scale(days_arr)
standardized_price = preprocessing.scale(price_arr)
standardized_market_value_mean = preprocessing.scale(market_value_mean_arr)
stadardized_market_value_std = preprocessing.scale(market_value_std_arr)
standardized_count_days = preprocessing.scale(count_days_arr)

# print(normalized_mileage.shape)

# print(make_column_encoder.toarray())
#create pipeline to run encoding 
#OneHotEncode our 
# [[7000 elements], 
# [7000 elements], 
# [7000 elements], 
# [7000 elements]]

standardized_X = pd.DataFrame([standardized_mileage, standardized_bids, standardized_days, standardized_market_value_mean, stadardized_market_value_std, standardized_count_days, sold_type_onehot, reserve_onehot]).T # , make_column_encoder, sold_type_column_encoder, reserve_column_encoder
# print(standardized_X)

# print(prelim_data)
prelim_data.to_csv("Data/prelim_data.csv", index=False)

y = prelim_data["Price"]
prelim_data.drop("Price", axis=1, inplace=True)
X = prelim_data

print(X)
print(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.33)

pipe.fit(X_train, y_train)
print(pipe.score(X_test, y_test))



# mod = GradientBoostingRegressor(n_estimators=500)
# mod.fit(X_train, y_train)

# print(mod.score(X_test, y_test))
# print(mod.feature_importances_)
