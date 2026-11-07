from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date, timedelta
from passlib.context import CryptContext
from shapely.geometry import Polygon, mapping
from geoalchemy2.shape import from_shape, to_shape
from pydantic import BaseModel

import models
import schemas
from database import engine, SessionLocal, get_db

# Ensure all tables are created in PostgreSQL
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SWARNABHOOMI API",
    description="Rice Production Intelligence & Demand Coordination Platform"
)

# --- CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- AUTOMATIC DATABASE SEEDER ON STARTUP ---
@app.on_event("startup")
def seed_initial_database():
    """Automatically creates default ID=1 records so Farmer and Buyer portals never hit ForeignKey errors."""
    db = SessionLocal()
    try:
        # 1. Seed Roles
        role_names = ["Farmer", "Agrarian", "Buyer", "Government"]
        for name in role_names:
            if not db.query(models.Role).filter(models.Role.name == name).first():
                db.add(models.Role(name=name))
        db.commit()

        farmer_role = db.query(models.Role).filter(models.Role.name == "Farmer").first()
        buyer_role = db.query(models.Role).filter(models.Role.name == "Buyer").first()

        # 2. Seed Default Users
        farmer_user = db.query(models.User).filter(models.User.username == "default_farmer").first()
        if not farmer_user:
            farmer_user = models.User(
                username="default_farmer",
                password_hash=pwd_context.hash("password123"),
                role_id=farmer_role.id if farmer_role else 1,
                status="Active"
            )
            db.add(farmer_user)
            db.commit()
            db.refresh(farmer_user)

        buyer_user = db.query(models.User).filter(models.User.username == "default_buyer").first()
        if not buyer_user:
            buyer_user = models.User(
                username="default_buyer",
                password_hash=pwd_context.hash("password123"),
                role_id=buyer_role.id if buyer_role else 1,
                status="Active"
            )
            db.add(buyer_user)
            db.commit()
            db.refresh(buyer_user)

        # 3. Seed Default Farmer (ID = 1) & Farm (ID = 1)
        farmer = db.query(models.Farmer).filter(models.Farmer.id == 1).first()
        if not farmer:
            farmer = models.Farmer(
                id=1,
                user_id=farmer_user.id,
                full_name="Sunil Perera",
                phone="0771234567",
                national_id="198512345678"
            )
            db.add(farmer)
            db.commit()
            db.refresh(farmer)

        farm = db.query(models.Farm).filter(models.Farm.id == 1).first()
        if not farm:
            farm = models.Farm(
                id=1,
                farmer_id=farmer.id,
                name="Anuradhapura Valley Farm",
                region="Anuradhapura",
                total_area=10.0
            )
            db.add(farm)
            db.commit()

        # 4. Seed Default Buyer (ID = 1)
        buyer = db.query(models.Buyer).filter(models.Buyer.id == 1).first()
        if not buyer:
            buyer = models.Buyer(
                id=1,
                user_id=buyer_user.id,
                company_name="Rajarata Rice Mills",
                organization_type="Miller",
                region="Anuradhapura",
                verified_status=True
            )
            db.add(buyer)
            db.commit()

        # 5. Seed Default Season (ID = 1)
        season = db.query(models.Season).filter(models.Season.id == 1).first()
        if not season:
            season = models.Season(
                id=1,
                name="Maha 2026/2027",
                year=2026,
                start_date=date(2026, 9, 1),
                end_date=date(2027, 3, 31),
                status="Active"
            )
            db.add(season)
            db.commit()

        # 6. Seed Default Rice Variety (ID = 1)
        variety = db.query(models.RiceVariety).filter(models.RiceVariety.id == 1).first()
        if not variety:
            variety = models.RiceVariety(
                id=1,
                name="Bg 352",
                variety_class="Short-Grain",
                maturity_days=105,
                average_yield_per_acre=2.2,
                water_requirement_level="Medium"
            )
            db.add(variety)
            db.commit()

    except Exception as e:
        db.rollback()
        print(f"Startup seeding warning: {e}")
    finally:
        db.close()


@app.get("/")
def health_check():
    return {
        "status": "SWARNABHOOMI Backend is online",
        "roles_supported": ["Farmer", "Agrarian", "Buyer", "Government"]
    }


# --- 1. ROLE INITIALIZATION ---
@app.post("/api/roles/seed", response_model=List[schemas.RoleResponse], tags=["System"])
def seed_roles(db: Session = Depends(get_db)):
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


# --- 4. SEASONS, VARIETIES & CULTIVATIONS ---
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

    # Automatically generate HarvestForecast when a cultivation is registered
    field = db.query(models.Field).filter(models.Field.id == db_cult.field_id).first()
    variety = db.query(models.RiceVariety).filter(models.RiceVariety.id == db_cult.variety_id).first()

    area_acres = field.area if field else 1.0
    yield_per_acre = (variety.average_yield_per_acre if variety and variety.average_yield_per_acre else 2.0)
    maturity_days = (variety.maturity_days if variety and variety.maturity_days else 105)

    est_start = db_cult.planting_date + timedelta(days=maturity_days)
    est_end = est_start + timedelta(days=14)
    est_qty = round(area_acres * yield_per_acre, 2)

    forecast = models.HarvestForecast(
        cultivation_id=db_cult.id,
        estimated_start_date=est_start,
        estimated_end_date=est_end,
        estimated_quantity=est_qty,
        confidence_level=0.85
    )
    db.add(forecast)
    db.commit()

    return db_cult


@app.get("/api/cultivations/{cultivation_id}/schedule", tags=["Farmer"])
def get_smart_schedule(cultivation_id: int, db: Session = Depends(get_db)):
    """Fetches the generated timeline and harvest forecast for a specific cultivation."""
    cultivation = db.query(models.Cultivation).filter(models.Cultivation.id == cultivation_id).first()
    forecast = db.query(models.HarvestForecast).filter(models.HarvestForecast.cultivation_id == cultivation_id).first()

    if not cultivation or not forecast:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return {
        "planting_date": cultivation.planting_date,
        "harvest_start": forecast.estimated_start_date,
        "harvest_end": forecast.estimated_end_date,
        "expected_yield_mt": forecast.estimated_quantity
    }


# --- 5. BUYER DEMAND ---
class BuyerDemandSimpleCreate(BaseModel):
    season_id: int = 1
    buyer_id: int = 1
    region: str
    variety_class: str
    quantity: float


@app.post("/api/demand", tags=["Buyer"])
def register_buyer_demand(demand: BuyerDemandSimpleCreate, db: Session = Depends(get_db)):
    """Registers a buyer's requirement for rice in a specific region."""
    new_demand = models.BuyerDemand(
        season_id=demand.season_id,
        buyer_id=demand.buyer_id,
        region=demand.region,
        variety_class=demand.variety_class,
        quantity=demand.quantity,
        status="Published"
    )
    db.add(new_demand)
    db.commit()
    db.refresh(new_demand)
    return {"message": "Demand registered successfully", "id": new_demand.id}


# --- 6. INTELLIGENCE & ANALYTICS OUTPUTS ---
@app.get("/api/forecast/harvest", response_model=List[schemas.HarvestForecastResponse], tags=["Analytics"])
def get_harvest_forecast(cultivation_id: int, db: Session = Depends(get_db)):
    return db.query(models.HarvestForecast).filter(models.HarvestForecast.cultivation_id == cultivation_id).all()


@app.get("/api/resources/plans", response_model=List[schemas.ResourcePlanResponse], tags=["Analytics"])
def get_resource_plans(cultivation_id: int, db: Session = Depends(get_db)):
    return db.query(models.ResourcePlan).filter(models.ResourcePlan.cultivation_id == cultivation_id).order_by(models.ResourcePlan.due_date).all()


@app.get("/api/analytics/supply-demand", tags=["Government"])
def get_market_balance(db: Session = Depends(get_db)):
    """Calculates the national/regional balance of rice supply vs demand."""
    total_supply = db.query(func.sum(models.HarvestForecast.estimated_quantity)).scalar() or 0.0
    total_demand = db.query(func.sum(models.BuyerDemand.quantity)).scalar() or 0.0
    balance = total_supply - total_demand

    return {
        "total_supply_mt": round(float(total_supply), 2),
        "total_demand_mt": round(float(total_demand), 2),
        "balance_mt": round(float(balance), 2),
        "status": "Critical Shortage" if balance < 0 else "Healthy Surplus"
    }