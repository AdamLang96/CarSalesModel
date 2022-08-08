from sqlalchemy import create_engine
import pandas as pd
import sklearn
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import GradientBoostingRegressor
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
print(full_data.shape)



#Model - Sparse <- encode car type, year made, etc. 
#Engine - <-  standardizable metrics like combustion volume and cylinder count, horsepower/kWh, electric (binary)
#Transmission 4WD/AWD,Manual <- Manual/Automatic  RWD, FWD (4wd is both)
#Location - Sparse (target encoding)

prelim_data = full_data[["Make", "Mileage", "Year", "Price", "Sold Type", "Num Bids", "Y_N_Reserve", 'Num_Days', 'Market_Value_Mean', 'Market_Value_Std', 'Count_Over_Days' ]]




y = prelim_data["Price"]
X = pd.concat([prelim_data[["Mileage", "Year", 'Market_Value_Mean', 'Market_Value_Std', 'Count_Over_Days']], 
                pd.get_dummies(prelim_data["Make"]), pd.get_dummies(prelim_data["Sold Type"]), pd.get_dummies(prelim_data["Y_N_Reserve"])], axis=1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.33)

mod = GradientBoostingRegressor(n_estimators=500)
mod.fit(X_train, y_train)
print(mod.score(X_test, y_test))
print(mod.feature_importances_)




