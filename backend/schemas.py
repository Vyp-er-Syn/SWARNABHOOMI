from pydantic import BaseModel, ConfigDict, Field as PydanticField
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- ROLE SCHEMAS ---
class RoleBase(BaseModel):
    name: str

class RoleResponse(RoleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- USER SCHEMAS ---
class UserBase(BaseModel):
    username: str
    role_id: int
    status: str = "Active"

class UserCreate(UserBase):
    password: str  # Plain password to be hashed before saving

class UserResponse(UserBase):
    id: int
    last_login: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

# --- FARMER SCHEMAS ---
class FarmerBase(BaseModel):
    identifier: str
    district_id: str
    gn_division_id: str
    contact: str

class FarmerCreate(FarmerBase):
    user_id: int

class FarmerResponse(FarmerBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

# --- BUYER SCHEMAS ---
class BuyerBase(BaseModel):
    buyer_type: str
    organization_name: str

class BuyerCreate(BuyerBase):
    user_id: int

class BuyerResponse(BuyerBase):
    id: int
    user_id: int
    verification_status: str
    model_config = ConfigDict(from_attributes=True)

# --- FARM & FIELD SCHEMAS ---
class FarmBase(BaseModel):
    name: str
    location: str

class FarmCreate(FarmBase):
    farmer_id: int

class FarmResponse(FarmBase):
    id: int
    farmer_id: int
    model_config = ConfigDict(from_attributes=True)

class FieldBase(BaseModel):
    name: str
    area: float
    water_regime_id: str
    soil_profile_id: str
    
class FieldCreate(FieldBase):
    farm_id: int
    # GeoJSON polygon coordinate array
    geometry_coordinates: List[List[List[float]]] 

class FieldResponse(FieldBase):
    id: int
    farm_id: int
    # Geometry returned as a GeoJSON dict
    geometry: Dict[str, Any] 
    model_config = ConfigDict(from_attributes=True)

    # --- SEASON (KANNA) SCHEMAS ---
class SeasonBase(BaseModel):
    name: str  # e.g., Maha / Yala
    year: int
    scope: str # e.g., Anuradhapura District
    planting_window_start: datetime
    planting_window_end: datetime
    status: str = "Draft"

class SeasonCreate(SeasonBase):
    pass

class SeasonResponse(SeasonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- RICE VARIETY SCHEMAS ---
class RiceVarietyBase(BaseModel):
    name: str  # e.g., BG 352
    duration_min_days: int
    duration_max_days: int
    maturity_class: str
    season_suitability: str
    yield_class: str
    water_regime_suitability: str

class RiceVarietyCreate(RiceVarietyBase):
    pass

class RiceVarietyResponse(RiceVarietyBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- CULTIVATION SCHEMAS ---
class CultivationBase(BaseModel):
    field_id: int
    season_id: int
    variety_id: int
    area: float
    planting_date: datetime
    status: str = "Planned"

class CultivationCreate(CultivationBase):
    pass

class CultivationResponse(CultivationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- BUYER DEMAND SCHEMAS ---
class BuyerDemandBase(BaseModel):
    buyer_id: int
    season_id: int
    variety_class: str
    quantity: float
    grade: str
    harvest_start: datetime
    harvest_end: datetime
    region: str
    status: str = "Published"

class BuyerDemandCreate(BuyerDemandBase):
    pass

class BuyerDemandResponse(BuyerDemandBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- RESOURCE & FORECAST SCHEMAS ---
class ResourcePlanResponse(BaseModel):
    id: int
    cultivation_id: int
    resource_type: str
    stage: str
    quantity: float
    due_date: datetime
    status: str
    model_config = ConfigDict(from_attributes=True)

class HarvestForecastResponse(BaseModel):
    id: int
    cultivation_id: int
    estimated_start_date: datetime
    estimated_end_date: datetime
    estimated_quantity: Optional[float] = None
    confidence: str
    model_config = ConfigDict(from_attributes=True)   