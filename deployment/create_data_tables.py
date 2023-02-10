from sqlalchemy import Column,  String, create_engine, Integer
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
Base = declarative_base()

class CarsAndBidsTable(Base):
    __tablename__ = 'cars_final'
    id = Column(Integer(), primary_key=True) 
    make  = Column(String())
    model  = Column(String())
    mileage  = Column(String())
    vin  = Column(String())
    status  = Column(String())
    location = Column(String())
    engine  = Column(String())
    drivetrain  = Column(String())
    transmission  = Column(String())
    bodystyle = Column(String())
    exteriorcolor = Column(String())
    interiorcolor = Column(String())
    price = Column(String())
    soldtype = Column(String())
    numbids = Column(String())
    y_n_reserve = Column(String())
    year = Column(String())
    date = Column(String())
    url = Column(String())
    
class VinAuditTable(Base):
    __tablename__ = 'vin_newest_final'
    id = Column(Integer(), primary_key=True)    
    vin = Column(String())
    market_value_mean = Column(String())
    market_value_std = Column(String())
    count = Column(String())
    count_over_days = Column(String())

class ModelsScore(Base):
    __tablename__ = 'models_score'
    id = Column(Integer(), primary_key=True)    
    date = Column(String())
    test_score = Column(String())
    environment = Column(String())
    
engine = create_engine("postgresql+psycopg2://codesmith:TensorFlow01?@database-1.ceq8tkxrvrbb.us-west-2.rds.amazonaws.com/postgres")
print(pd.read_sql_table('cars_final', engine))
