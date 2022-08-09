from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import sklearn as sk
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn.compose import make_column_transformer
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
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

prelim_data = full_data[["Make", "Mileage", "Year", "Price", "Sold Type", "Num Bids", "Y_N_Reserve", 'Num_Days', 'Market_Value_Mean', 'Market_Value_Std', 'Count_Over_Days' ]]

# print(prelim_data.dtypes)

ohe = OneHotEncoder()
label_encoder = LabelEncoder()

make_column_encoder = ohe.fit_transform(prelim_data[['Make']])
sold_type_column_encoder = ohe.fit_transform(prelim_data[['Sold Type']])
reserve_column_encoder = ohe.fit_transform(prelim_data[['Y_N_Reserve']])

mileage_arr = np.array(prelim_data['Mileage'])
num_bids_arr = np.array(prelim_data['Num Bids'])
days_arr = np.array(prelim_data['Num_Days'])
price_arr = np.array(prelim_data['Price'])




normalized_mileage = preprocessing.scale([mileage_arr])
normalized_bids = preprocessing.scale([num_bids_arr])
normalized_days = preprocessing.scale([days_arr])
normalized_price = preprocessing.scale([price_arr])


# print(make_column_encoder.toarray())
#create pipeline to run encoding 
#OneHotEncode our 

# print(prelim_data)
prelim_data.to_csv("Data/prelim_data.csv", index=False)

y = prelim_data["Price"]
X = pd.concat([prelim_data[["Mileage", "Year", 'Market_Value_Mean', 'Market_Value_Std', 'Count_Over_Days']], 
                pd.get_dummies(prelim_data["Make"]), pd.get_dummies(prelim_data["Sold Type"]), pd.get_dummies(prelim_data["Y_N_Reserve"])], axis=1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.33)

mod = GradientBoostingRegressor(n_estimators=500)
mod.fit(X_train, y_train)
# print(mod.score(X_test, y_test))
# print(mod.feature_importances_)




