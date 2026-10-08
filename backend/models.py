from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from database import Base
import datetime

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g., Farmer, Agrarian, Buyer, Government

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"))
    status = Column(String, default="Active")
    last_login = Column(DateTime, default=datetime.datetime.utcnow)

class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    identifier = Column(String, unique=True) # NIC or local identifier
    district_id = Column(String)
    gn_division_id = Column(String)
    contact = Column(String)

class Buyer(Base):
    __tablename__ = "buyers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    buyer_type = Column(String) # Government or Third-party
    organization_name = Column(String)
    verification_status = Column(String, default="Pending")

class Farm(Base):
    __tablename__ = "farms"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    name = Column(String)
    location = Column(String)

class Field(Base):
    __tablename__ = "fields"
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    name = Column(String)
    area = Column(Float)
    # PostGIS Geometry column for field boundaries (SRID 4326 for standard GPS coordinates)
    geometry = Column(Geometry(geometry_type='POLYGON', srid=4326, spatial_index=False))
    water_regime_id = Column(String)
    soil_profile_id = Column(String)

# ... (append to existing models.py) ...

class Season(Base):
    __tablename__ = "seasons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # Maha / Yala
    year = Column(Integer)
    scope = Column(String) # District / ASC
    planting_window_start = Column(DateTime)
    planting_window_end = Column(DateTime)
    status = Column(String, default="Draft")

class RiceVariety(Base):
    __tablename__ = "rice_varieties"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    duration_min_days = Column(Integer)
    duration_max_days = Column(Integer)
    maturity_class = Column(String)
    season_suitability = Column(String)
    yield_class = Column(String)
    water_regime_suitability = Column(String)

class Cultivation(Base):
    __tablename__ = "cultivations"
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"))
    season_id = Column(Integer, ForeignKey("seasons.id"))
    variety_id = Column(Integer, ForeignKey("rice_varieties.id"))
    area = Column(Float)
    planting_date = Column(DateTime)
    status = Column(String, default="Planned")

class BuyerDemand(Base):
    __tablename__ = "buyer_demands"
    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("buyers.id"))
    season_id = Column(Integer, ForeignKey("seasons.id"))
    variety_class = Column(String)
    quantity = Column(Float) # in MT
    grade = Column(String)
    harvest_start = Column(DateTime)
    harvest_end = Column(DateTime)
    region = Column(String)
    status = Column(String, default="Published")