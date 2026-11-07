from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, text, inspect
from typing import List
from datetime import date, timedelta
from shapely.geometry import Polygon, mapping
from geoalchemy2.shape import from_shape, to_shape
from pydantic import BaseModel

import models
import schemas
from database import engine, SessionLocal, get_db

# 1. Create any completely missing tables
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


def sync_schema_and_seed(db: Session):
    """
    1. Automatically adds any missing columns defined in models.py to existing PostgreSQL tables.
    2. Relaxes any legacy NOT NULL columns not present in models.py.
    3. Seeds all ID=1 baseline records in isolated transactions so Farmer, Buyer, and Government portals work seamlessly.
    """
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    type_map = {
        "INTEGER": "INTEGER",
        "VARCHAR": "VARCHAR(255)",
        "FLOAT": "DOUBLE PRECISION",
        "BOOLEAN": "BOOLEAN",
        "DATE": "DATE",
        "DATETIME": "TIMESTAMPTZ",
    }

    # Step A: Synchronize table columns with models.py
    for table_name, table in models.Base.metadata.tables.items():
        if table_name in existing_tables:
            existing_cols = {col["name"]: col for col in inspector.get_columns(table_name)}
            model_col_names = {col.name for col in table.columns}

            # Add any missing columns defined in models.py
            for col in table.columns:
                if col.name not in existing_cols:
                    col_type_key = col.type.__class__.__name__.upper()
                    sql_type = type_map.get(col_type_key, "VARCHAR(255)")
                    try:
                        db.execute(text(f'ALTER TABLE "{table_name}" ADD COLUMN IF NOT EXISTS "{col.name}" {sql_type};'))
                        db.commit()
                    except Exception as e:
                        db.rollback()
                        print(f"Column add note ({table_name}.{col.name}): {e}")

            # Drop NOT NULL constraint on any obsolete columns from older migrations
            for existing_col_name, existing_col_info in existing_cols.items():
                if existing_col_name not in model_col_names and existing_col_name != "id":
                    if not existing_col_info.get("nullable", True):
                        try:
                            db.execute(text(f'ALTER TABLE "{table_name}" ALTER COLUMN "{existing_col_name}" DROP NOT NULL;'))
                            db.commit()
                        except Exception as e:
                            db.rollback()

    # Step B: Seed Roles (IDs 1..4)
    role_data = [(1, "Farmer"), (2, "Agrarian"), (3, "Buyer"), (4, "Government")]
    for r_id, r_name in role_data:
        try:
            if not db.query(models.Role).filter((models.Role.id == r_id) | (models.Role.name == r_name)).first():
                db.add(models.Role(id=r_id, name=r_name))
                db.commit()
        except Exception:
            db.rollback()

    farmer_role = db.query(models.Role).filter(models.Role.name == "Farmer").first()
    buyer_role = db.query(models.Role).filter(models.Role.name == "Buyer").first()

    # Step C: Seed Default Users
    try:
        farmer_user = db.query(models.User).filter(models.User.username == "default_farmer").first()
        if not farmer_user:
            farmer_user = models.User(
                username="default_farmer",
                password_hash="hashed_pw_123",
                role_id=farmer_role.id if farmer_role else 1,
                status="Active"
            )
            db.add(farmer_user)
            db.commit()
            db.refresh(farmer_user)
    except Exception as e:
        db.rollback()
        farmer_user = db.query(models.User).first()

    try:
        buyer_user = db.query(models.User).filter(models.User.username == "default_buyer").first()
        if not buyer_user:
            buyer_user = models.User(
                username="default_buyer",
                password_hash="hashed_pw_123",
                role_id=buyer_role.id if buyer_role else 1,
                status="Active"
            )
            db.add(buyer_user)
            db.commit()
            db.refresh(buyer_user)
    except Exception as e:
        db.rollback()
        buyer_user = db.query(models.User).first()

    # Step D: Seed WaterRegime (ID=1) & SoilProfile (ID=1) required by FieldMap.tsx
    try:
        if not db.query(models.WaterRegime).filter(models.WaterRegime.id == 1).first():
            db.add(models.WaterRegime(id=1, name="Irrigated", description="Major and minor irrigation schemes"))
            db.commit()
    except Exception:
        db.rollback()

    try:
        if not db.query(models.SoilProfile).filter(models.SoilProfile.id == 1).first():
            db.add(models.SoilProfile(id=1, soil_type="Reddish Brown Earth", drainage_class="Well Drained", fertility_rating="High"))
            db.commit()
    except Exception:
        db.rollback()

    # Step E: Seed Default Buyer (ID=1) required by BuyerDemandForm.tsx
    try:
        if not db.query(models.Buyer).filter(models.Buyer.id == 1).first():
            db.add(models.Buyer(
                id=1,
                user_id=buyer_user.id if buyer_user else 1,
                company_name="Rajarata Rice Mills",
                organization_type="Miller",
                region="Anuradhapura",
                verified_status=True
            ))
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Seed Buyer warning: {e}")

    # Step F: Seed Default Farmer (ID=1) & Farm (ID=1) required by FieldMap.tsx
    try:
        if not db.query(models.Farmer).filter(models.Farmer.id == 1).first():
            db.add(models.Farmer(
                id=1,
                user_id=farmer_user.id if farmer_user else 1,
                full_name="Sunil Perera",
                phone="0771234567",
                national_id="198512345678"
            ))
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Seed Farmer warning: {e}")

    try:
        if not db.query(models.Farm).filter(models.Farm.id == 1).first():
            db.add(models.Farm(
                id=1,
                farmer_id=1,
                name="Anuradhapura Valley Farm",
                region="Anuradhapura",
                total_area=10.0
            ))
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Seed Farm warning: {e}")

    # Step G: Seed Default Season (ID=1) & RiceVariety (ID=1)
    try:
        if not db.query(models.Season).filter(models.Season.id == 1).first():
            db.add(models.Season(
                id=1,
                name="Maha 2026/2027",
                year=2026,
                start_date=date(2026, 9, 1),
                end_date=date(2027, 3, 31),
                status="Active"
            ))
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Seed Season warning: {e}")

    try:
        if not db.query(models.RiceVariety).filter(models.RiceVariety.id == 1).first():
            db.add(models.RiceVariety(
                id=1,
                name="Bg 352",
                variety_class="Short-Grain",
                maturity_days=105,
                average_yield_per_acre=2.2,
                water_requirement_level="Medium"
            ))
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Seed Variety warning: {e}")


@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        sync_schema_and_seed(db)
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
    sync_schema_and_seed(db)
    return db.query(models.Role).all()


# --- 2. USERS, FARMERS & BUYERS ---
@app.post("/api/users", response_model=schemas.UserResponse, tags=["Users & Auth"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = models.User(
        username=user.username,
        password_hash=user.password,
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
    sync_schema_and_seed(db)
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
    sync_schema_and_seed(db)

    field = db.query(models.Field).filter(models.Field.id == cultivation.field_id).first()
    variety = db.query(models.RiceVariety).filter(models.RiceVariety.id == cultivation.variety_id).first()

    area_acres = field.area if field else 1.0
    yield_per_acre = (variety.average_yield_per_acre if variety and variety.average_yield_per_acre else 2.2)
    maturity_days = (variety.maturity_days if variety and variety.maturity_days else 105)

    est_start = cultivation.planting_date + timedelta(days=maturity_days)
    est_end = est_start + timedelta(days=14)
    est_qty = round(area_acres * yield_per_acre, 2)

    db_cult = models.Cultivation(
        field_id=cultivation.field_id,
        season_id=cultivation.season_id,
        variety_id=cultivation.variety_id,
        planting_date=cultivation.planting_date,
        expected_harvest_date=est_start,
        status=cultivation.status
    )
    db.add(db_cult)
    db.commit()
    db.refresh(db_cult)

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
    sync_schema_and_seed(db)

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