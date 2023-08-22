from sqlalchemy import Column,  String, Integer
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class CarsAndBidsTable(Base):
    __tablename__ = 'cars_bids_listings'
    id = Column(Integer(), primary_key=True) 
    make  = Column(String())
    model  = Column(String())
    mileage  = Column(String())
    vin  = Column(String())          
    title_status  = Column(String())
    location = Column(String())
    engine  = Column(String())
    drivetrain  = Column(String())
    transmission  = Column(String())
    body_style = Column(String())
    exterior_color = Column(String())
    interior_color = Column(String())
    price = Column(String())
    sold_type = Column(String())
    num_bids = Column(String())
    y_n_reserve = Column(String())
    year = Column(String())
    date = Column(String())
    url = Column(String())
    
class VinAuditTable(Base):
    __tablename__ = 'vin_audit_data'
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


