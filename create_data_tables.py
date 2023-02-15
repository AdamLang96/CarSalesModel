from sqlalchemy import Column,  String, create_engine, Integer, text, inspect
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
import pandas as pd

class CarsAndBidsTable(Base):
    __tablename__ = 'cars_bids_listings'
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
    path = Column(String())
    test_score = Column(String())
    environment = Column(String())
    
con = create_engine("postgresql+psycopg2://postgres:postgres@classical-project.ceq8tkxrvrbb.us-west-2.rds.amazonaws.com/postgres")
print(pd.read_sql_table('cars_bids_listings', con))
# Base.metadata.create_all(con)

