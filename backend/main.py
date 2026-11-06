from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from passlib.context import CryptContext
from shapely.geometry import Polygon, mapping
from geoalchemy2.shape import from_shape, to_shape

import models
import schemas
from database import get_db

app = FastAPI(
    title="SWARNABHOOMI API",
    description="Rice Production Intelligence & Demand Coordination Platform"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.get("/")
def health_check():
    return {
        "status": "SWARNABHOOMI Backend is online",
        "roles_supported": ["Farmer", "Agrarian", "Buyer", "Government"]
    }

# --- 1. ROLE INITIALIZATION ---
@app.post("/api/roles/seed", response_model=List[schemas.RoleResponse], tags=["System"])
def seed_roles(db: Session = Depends(get_db)):
    """Initializes the 4 strict application roles if they don't exist."""
    role_names = ["Farmer", "Agrarian", "Buyer", "Government"]
    created_roles = []
    for name in role_names:
        role = db.query(models.Role).filter(models.Role.name == name).first()
        if not role:
            role = models.Role(name=name)
            db.add(role)
            db.commit()
            db.refresh(role)
        created_roles.append(role)
    return created_roles

# --- 2. USERS, FARMERS & BUYERS ---
@app.post("/api/users", response_model=schemas.UserResponse, tags=["Users & Auth"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        password_hash=hashed_pw,
        role_id=user.role_id,
        status=user.status
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/farmers", response_model=schemas.FarmerResponse, tags=["Farmers"])
def create_farmer(farmer: schemas.FarmerCreate, db: Session = Depends(get_db)):
    db_farmer = models.Farmer(**farmer.model_dump())
    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return db_farmer

@app.post("/api/buyers", response_model=schemas.BuyerResponse, tags=["Buyers"])
def create_buyer(buyer: schemas.BuyerCreate, db: Session = Depends(get_db)):
    db_buyer = models.Buyer(**buyer.model_dump())
    db.add(db_buyer)
    db.commit()
    db.refresh(db_buyer)
    return db_buyer

# --- 3. FARMS & SPATIAL FIELDS (POSTGIS) ---
@app.post("/api/farms", response_model=schemas.FarmResponse, tags=["Farms & Fields"])
def create_farm(farm: schemas.FarmCreate, db: Session = Depends(get_db)):
    db_farm = models.Farm(**farm.model_dump())
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    return db_farm

@app.post("/api/fields", response_model=schemas.FieldResponse, tags=["Farms & Fields"])
def create_field(field_in: schemas.FieldCreate, db: Session = Depends(get_db)):
    try:
        # Convert coordinate ring [[[lon, lat], ...]] to a Shapely Polygon
        poly = Polygon(field_in.geometry_coordinates[0])
        wkt_geom = from_shape(poly, srid=4326)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid polygon coordinates: {str(e)}")

    db_field = models.Field(
        farm_id=field_in.farm_id,
        name=field_in.name,
        area=field_in.area,
        geometry=wkt_geom,
        water_regime_id=field_in.water_regime_id,
        soil_profile_id=field_in.soil_profile_id
    )
    db.add(db_field)
    db.commit()
    db.refresh(db_field)

    # Convert stored PostGIS geometry back to GeoJSON format for the response
    shapely_geom = to_shape(db_field.geometry)
    return {
        "id": db_field.id,
        "farm_id": db_field.farm_id,
        "name": db_field.name,
        "area": db_field.area,
        "water_regime_id": db_field.water_regime_id,
        "soil_profile_id": db_field.soil_profile_id,
        "geometry": mapping(shapely_geom)
    }

@app.get("/api/fields", response_model=List[schemas.FieldResponse], tags=["Farms & Fields"])
def get_fields(db: Session = Depends(get_db)):
    fields = db.query(models.Field).all()
    results = []
    for f in fields:
        shapely_geom = to_shape(f.geometry)
        results.append({
            "id": f.id,
            "farm_id": f.farm_id,
            "name": f.name,
            "area": f.area,
            "water_regime_id": f.water_regime_id,
            "soil_profile_id": f.soil_profile_id,
            "geometry": mapping(shapely_geom)
        })
    return results

# --- 4. SEASONS, VARIETIES, CULTIVATIONS & DEMAND ---
@app.post("/api/seasons", response_model=schemas.SeasonResponse, tags=["Seasons & Varieties"])
def create_season(season: schemas.SeasonCreate, db: Session = Depends(get_db)):
    db_season = models.Season(**season.model_dump())
    db.add(db_season)
    db.commit()
    db.refresh(db_season)
    return db_season

@app.post("/api/rice-varieties", response_model=schemas.RiceVarietyResponse, tags=["Seasons & Varieties"])
def create_variety(variety: schemas.RiceVarietyCreate, db: Session = Depends(get_db)):
    db_variety = models.RiceVariety(**variety.model_dump())
    db.add(db_variety)
    db.commit()
    db.refresh(db_variety)
    return db_variety

@app.get("/api/rice-varieties", response_model=List[schemas.RiceVarietyResponse], tags=["Seasons & Varieties"])
def list_varieties(db: Session = Depends(get_db)):
    return db.query(models.RiceVariety).all()

@app.post("/api/cultivations", response_model=schemas.CultivationResponse, tags=["Cultivations & Demand"])
def create_cultivation(cultivation: schemas.CultivationCreate, db: Session = Depends(get_db)):
    db_cult = models.Cultivation(**cultivation.model_dump())
    db.add(db_cult)
    db.commit()
    db.refresh(db_cult)
    return db_cult

@app.post("/api/demands", response_model=schemas.BuyerDemandResponse, tags=["Cultivations & Demand"])
def create_demand(demand: schemas.BuyerDemandCreate, db: Session = Depends(get_db)):
    db_demand = models.BuyerDemand(**demand.model_dump())
    db.add(db_demand)
    db.commit()
    db.refresh(db_demand)
    return db_demand

# --- 5. INTELLIGENCE & ANALYTICS OUTPUTS ---
@app.get("/api/forecast/harvest", response_model=List[schemas.HarvestForecastResponse], tags=["Analytics"])
def get_harvest_forecast(cultivation_id: int, db: Session = Depends(get_db)):
    return db.query(models.HarvestForecast).filter(models.HarvestForecast.cultivation_id == cultivation_id).all()

@app.get("/api/resources/plans", response_model=List[schemas.ResourcePlanResponse], tags=["Analytics"])
def get_resource_plans(cultivation_id: int, db: Session = Depends(get_db)):
    return db.query(models.ResourcePlan).filter(models.ResourcePlan.cultivation_id == cultivation_id).order_by(models.ResourcePlan.due_date).all()

# Append to backend/main.py
@app.get("/api/analytics/supply-demand", response_model=schemas.SupplyDemandBalanceResponse, tags=["Analytics"])
def get_supply_demand_balance(season_id: int, region: str, variety_class: str, db: Session = Depends(get_db)):
    """
    Returns the rice balance status by comparing expected production against demand[cite: 32].
    """
    return intelligence.calculate_supply_demand_balance(db, season_id, region, variety_class)


# Append to backend/main.py
@app.get("/api/cultivations/{cultivation_id}/schedule", tags=["Farmer"])
def get_smart_schedule(cultivation_id: int, db: Session = Depends(get_db)):
    """Fetches the generated timeline and harvest forecast for a specific cultivation."""
    cultivation = db.query(models.Cultivation).filter(models.Cultivation.id == cultivation_id).first()
    forecast = db.query(models.HarvestForecast).filter(models.HarvestForecast.cultivation_id == cultivation_id).first()
    
    if not cultivation or not forecast:
        return {"error": "Schedule not found"}
        
    return {
        "planting_date": cultivation.planting_date,
        "harvest_start": forecast.estimated_start_date,
        "harvest_end": forecast.estimated_end_date,
        "expected_yield_mt": forecast.estimated_quantity
    }