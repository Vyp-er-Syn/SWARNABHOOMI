from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from database import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    status = Column(String(20), default="Active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    role = relationship("Role")

class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    national_id = Column(String(20), unique=True)
    user = relationship("User")
    farms = relationship("Farm", back_populates="farmer")

class Buyer(Base):
    __tablename__ = "buyers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company_name = Column(String(100), nullable=False)
    organization_type = Column(String(50))
    region = Column(String(50))
    verified_status = Column(Boolean, default=False)
    user = relationship("User")

class WaterRegime(Base):
    __tablename__ = "water_regimes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

class SoilProfile(Base):
    __tablename__ = "soil_profiles"
    id = Column(Integer, primary_key=True, index=True)
    soil_type = Column(String(50), unique=True, nullable=False)
    drainage_class = Column(String(50))
    fertility_rating = Column(String(50))

class Farm(Base):
    __tablename__ = "farms"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    name = Column(String(100))
    region = Column(String(50), nullable=False)
    total_area = Column(Float)
    farmer = relationship("Farmer", back_populates="farms")
    fields = relationship("Field", back_populates="farm")

class Field(Base):
    __tablename__ = "fields"
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    name = Column(String(100))
    area = Column(Float, nullable=False)
    geometry = Column(Geometry(geometry_type='POLYGON', srid=4326), nullable=False)
    water_regime_id = Column(Integer, ForeignKey("water_regimes.id"))
    soil_profile_id = Column(Integer, ForeignKey("soil_profiles.id"))
    farm = relationship("Farm", back_populates="fields")
    water_regime = relationship("WaterRegime")
    soil_profile = relationship("SoilProfile")

class Season(Base):
    __tablename__ = "seasons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), default="Upcoming")

class RiceVariety(Base):
    __tablename__ = "rice_varieties"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    variety_class = Column(String(50), nullable=False)
    maturity_days = Column(Integer, nullable=False)
    average_yield_per_acre = Column(Float, nullable=False)
    water_requirement_level = Column(String(50))

class Cultivation(Base):
    __tablename__ = "cultivations"
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    variety_id = Column(Integer, ForeignKey("rice_varieties.id"), nullable=False)
    planting_date = Column(Date, nullable=False)
    expected_harvest_date = Column(Date)
    status = Column(String(20), default="Planned")
    field = relationship("Field")
    season = relationship("Season")
    variety = relationship("RiceVariety")

class BuyerDemand(Base):
    __tablename__ = "buyer_demands"
    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    variety_class = Column(String(50), nullable=False)
    quantity = Column(Float, nullable=False)
    grade = Column(String(20))
    harvest_start = Column(Date)
    harvest_end = Column(Date)
    region = Column(String(50), nullable=False)
    status = Column(String(20), default="Published")
    buyer = relationship("Buyer")
    season = relationship("Season")

class ResourceRule(Base):
    __tablename__ = "resource_rules"
    id = Column(Integer, primary_key=True, index=True)
    variety_id = Column(Integer, ForeignKey("rice_varieties.id"), nullable=False)
    stage_name = Column(String(50), nullable=False)
    days_after_planting = Column(Integer, nullable=False)
    input_type = Column(String(50), nullable=False)
    input_name = Column(String(100), nullable=False)
    quantity_per_acre = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    variety = relationship("RiceVariety")

class ResourcePlan(Base):
    __tablename__ = "resource_plans"
    id = Column(Integer, primary_key=True, index=True)
    cultivation_id = Column(Integer, ForeignKey("cultivations.id"), nullable=False)
    task_type = Column(String(50), nullable=False)
    recommended_input = Column(String(100), nullable=False)
    due_date = Column(Date, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    status = Column(String(20), default="Pending")
    cultivation = relationship("Cultivation")

class HarvestForecast(Base):
    __tablename__ = "harvest_forecasts"
    id = Column(Integer, primary_key=True, index=True)
    cultivation_id = Column(Integer, ForeignKey("cultivations.id"), unique=True, nullable=False)
    estimated_start_date = Column(Date, nullable=False)
    estimated_end_date = Column(Date, nullable=False)
    estimated_quantity = Column(Float, nullable=False)
    confidence_level = Column(Float, default=0.85)
    cultivation = relationship("Cultivation")