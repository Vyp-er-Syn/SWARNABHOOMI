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
    geometry = Column(Geometry(geometry_type='POLYGON', srid=4326))
    water_regime_id = Column(String)
    soil_profile_id = Column(String)