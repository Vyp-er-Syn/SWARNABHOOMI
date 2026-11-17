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

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SWARNABHOOMI API",
    description="Rice Production Intelligence & Demand Coordination Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def sync_schema_and_seed(db: Session):
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

    for table_name, table in models.Base.metadata.tables.items():
        if table_name in existing_tables:
            existing_cols = {col["name"]: col for col in inspector.get_columns(table_name)}
            model_col_names = {col.name for col in table.columns}

            for col in table.columns:
                if col.name not in existing_cols:
                    col_type_key = col.type.__class__.__name__.upper()
                    sql_type = type_map.get(col_type_key, "VARCHAR(255)")
                    try:
                        db.execute(text(f'ALTER TABLE "{table_name}" ADD COLUMN IF NOT EXISTS "{col.name}" {sql_type};'))
                        db.commit()
                    except Exception:
                        db.rollback()

            for existing_col_name, existing_col_info in existing_cols.items():
                if existing_col_name not in model_col_names and existing_col_name != "id":
                    if not existing_col_info.get("nullable", True):
                        try:
                            db.execute(text(f'ALTER TABLE "{table_name}" ALTER COLUMN "{existing_col_name}" DROP NOT NULL;'))
                            db.commit()
                        except Exception:
                            db.rollback()

    # Seed Roles
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

    # Seed Default Users
     # Step C: Seed Default Users for all 4 Portals
    default_users = [
        ("default_farmer", "Farmer"),
        ("default_agrarian", "Agrarian"),
        ("default_buyer", "Buyer"),
        ("default_gov", "Government"),
    ]
    for uname, rname in default_users:
        try:
            role_obj = db.query(models.Role).filter(models.Role.name == rname).first()
            if not db.query(models.User).filter(models.User.username == uname).first():
                db.add(models.User(
                    username=uname,
                    password_hash="hashed_pw_123",
                    role_id=role_obj.id if role_obj else 1,
                    status="Active"
                ))
                db.commit()
        except Exception:
            db.rollback()

    farmer_user = db.query(models.User).filter(models.User.username == "default_farmer").first()
    buyer_user = db.query(models.User).filter(models.User.username == "default_buyer").first()

    # Seed Water Regimes & Soil Profiles
    water_regimes = [
        (1, "Irrigated", "Major and minor irrigation schemes"),
        (2, "Rainfed", "Dependent on seasonal monsoon rainfall"),
    ]
    for w_id, w_name, w_desc in water_regimes:
        try:
            if not db.query(models.WaterRegime).filter(models.WaterRegime.id == w_id).first():
                db.add(models.WaterRegime(id=w_id, name=w_name, description=w_desc))
                db.commit()
        except Exception:
            db.rollback()

    soil_profiles = [
        (1, "Reddish Brown Earth", "Well Drained", "High"),
        (2, "Low Humic Gley", "Poorly Drained", "Medium"),
        (3, "Alluvial", "Moderately Drained", "High"),
    ]
    for s_id, s_type, s_drain, s_fert in soil_profiles:
        try:
            if not db.query(models.SoilProfile).filter(models.SoilProfile.id == s_id).first():
                db.add(models.SoilProfile(id=s_id, soil_type=s_type, drainage_class=s_drain, fertility_rating=s_fert))
                db.commit()
        except Exception:
            db.rollback()

    # Seed Default Buyer, Farmer & Farm
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
    except Exception:
        db.rollback()

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
    except Exception:
        db.rollback()

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
    except Exception:
        db.rollback()

    # Seed Default Season
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
    except Exception:
        db.rollback()

    # Seed Sri Lankan Rice Varieties
    varieties_seed = [
        (1, "Bg 352", "Short-Grain (Nadu)", 105, 2.2, "Medium"),
        (2, "Bg 300", "Short-Grain (Nadu)", 90, 2.0, "Low"),
        (3, "Bg 360", "Samba", 105, 1.9, "Medium"),
        (4, "At 362", "Long-Grain (Red/White)", 105, 2.4, "Medium"),
        (5, "Suwandel", "Traditional (Heenati, Suwandel)", 120, 1.4, "High"),
    ]
    for v_id, v_name, v_class, v_days, v_yield, v_water in varieties_seed:
        try:
            if not db.query(models.RiceVariety).filter((models.RiceVariety.id == v_id) | (models.RiceVariety.name == v_name)).first():
                db.add(models.RiceVariety(
                    id=v_id,
                    name=v_name,
                    variety_class=v_class,
                    maturity_days=v_days,
                    average_yield_per_acre=v_yield,
                    water_requirement_level=v_water
                ))
                db.commit()
        except Exception:
            db.rollback()

    # Seed Agronomic Resource Rules for each variety
    try:
        if db.query(models.ResourceRule).count() == 0:
            all_varieties = db.query(models.RiceVariety).all()
            for v in all_varieties:
                rules = [
                    models.ResourceRule(variety_id=v.id, stage_name="Basal Dressing", days_after_planting=0, input_type="Fertilizer", input_name="TSP (Triple Super Phosphate)", quantity_per_acre=22.0, unit="kg"),
                    models.ResourceRule(variety_id=v.id, stage_name="1st Top Dressing (Vegetative)", days_after_planting=14, input_type="Fertilizer", input_name="Urea", quantity_per_acre=30.0, unit="kg"),
                    models.ResourceRule(variety_id=v.id, stage_name="2nd Top Dressing (Tillering)", days_after_planting=28, input_type="Fertilizer", input_name="Urea + MOP", quantity_per_acre=45.0, unit="kg"),
                    models.ResourceRule(variety_id=v.id, stage_name="3rd Top Dressing (Panicle Initiation)", days_after_planting=42, input_type="Fertilizer", input_name="Urea + MOP", quantity_per_acre=35.0, unit="kg"),
                ]
                db.add_all(rules)
            db.commit()
    except Exception:
        db.rollback()

    # Sync PostgreSQL sequences
    for tbl in ["roles", "users", "water_regimes", "soil_profiles", "farmers", "farms", "buyers", "seasons", "rice_varieties", "resource_rules"]:
        try:
            db.execute(text(f"SELECT setval(pg_get_serial_sequence('{tbl}', 'id'), COALESCE((SELECT MAX(id) FROM {tbl}), 1), true);"))
            db.commit()
        except Exception:
            db.rollback()


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


@app.get("/api/catalog/varieties", tags=["Seasons & Varieties"])
def get_variety_catalog(db: Session = Depends(get_db)):
    varieties = db.query(models.RiceVariety).order_by(models.RiceVariety.id).all()
    return [
        {
            "id": v.id,
            "name": v.name,
            "variety_class": v.variety_class,
            "maturity_days": v.maturity_days,
            "average_yield_per_acre": v.average_yield_per_acre,
            "water_requirement_level": v.water_requirement_level,
        }
        for v in varieties
    ]


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


@app.post("/api/cultivations", response_model=schemas.CultivationResponse, tags=["Cultivations & Demand"])
def create_cultivation(cultivation: schemas.CultivationCreate, db: Session = Depends(get_db)):
    field = db.query(models.Field).filter(models.Field.id == cultivation.field_id).first()
    variety = db.query(models.RiceVariety).filter(models.RiceVariety.id == cultivation.variety_id).first()

    area_acres = field.area if field else 1.0
    yield_per_acre = (variety.average_yield_per_acre if variety and variety.average_yield_per_acre else 2.2)
    maturity_days = (variety.maturity_days if variety and variety.maturity_days else 105)

    p_date = cultivation.planting_date.date() if hasattr(cultivation.planting_date, "date") else cultivation.planting_date
    est_start = p_date + timedelta(days=maturity_days)
    est_end = est_start + timedelta(days=14)
    est_qty = round(area_acres * yield_per_acre, 2)

    db_cult = models.Cultivation(
        field_id=cultivation.field_id,
        season_id=cultivation.season_id,
        variety_id=cultivation.variety_id,
        planting_date=p_date,
        expected_harvest_date=est_start,
        status=cultivation.status
    )
    db.add(db_cult)
    db.commit()
    db.refresh(db_cult)

    # 1. Generate Harvest Forecast
    forecast = models.HarvestForecast(
        cultivation_id=db_cult.id,
        estimated_start_date=est_start,
        estimated_end_date=est_end,
        estimated_quantity=est_qty,
        confidence_level=0.85
    )
    db.add(forecast)

    # 2. Generate Stage-by-Stage Agronomic Resource Plans
    rules = db.query(models.ResourceRule).filter(models.ResourceRule.variety_id == db_cult.variety_id).all()
    for rule in rules:
        plan = models.ResourcePlan(
            cultivation_id=db_cult.id,
            task_type=f"{rule.stage_name} ({rule.input_type})",
            recommended_input=rule.input_name,
            due_date=p_date + timedelta(days=rule.days_after_planting),
            quantity=round(rule.quantity_per_acre * area_acres, 2),
            unit=rule.unit,
            status="Scheduled"
        )
        db.add(plan)

    db.commit()
    return db_cult


@app.get("/api/cultivations/{cultivation_id}/schedule", tags=["Farmer"])
def get_smart_schedule(cultivation_id: int, db: Session = Depends(get_db)):
    cultivation = db.query(models.Cultivation).filter(models.Cultivation.id == cultivation_id).first()
    forecast = db.query(models.HarvestForecast).filter(models.HarvestForecast.cultivation_id == cultivation_id).first()
    plans = db.query(models.ResourcePlan).filter(models.ResourcePlan.cultivation_id == cultivation_id).order_by(models.ResourcePlan.due_date).all()
    variety = db.query(models.RiceVariety).filter(models.RiceVariety.id == cultivation.variety_id).first() if cultivation else None

    if not cultivation or not forecast:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return {
        "cultivation_id": cultivation.id,
        "variety_name": variety.name if variety else "Bg 352",
        "maturity_days": variety.maturity_days if variety else 105,
        "planting_date": cultivation.planting_date,
        "harvest_start": forecast.estimated_start_date,
        "harvest_end": forecast.estimated_end_date,
        "expected_yield_mt": forecast.estimated_quantity,
        "resource_plans": [
            {
                "id": p.id,
                "task_type": p.task_type,
                "recommended_input": p.recommended_input,
                "due_date": p.due_date,
                "quantity": p.quantity,
                "unit": p.unit,
                "status": p.status
            }
            for p in plans
        ]
    }


class BuyerDemandSimpleCreate(BaseModel):
    season_id: int = 1
    buyer_id: int = 1
    region: str
    variety_class: str
    quantity: float


@app.post("/api/demand", tags=["Buyer"])
def register_buyer_demand(demand: BuyerDemandSimpleCreate, db: Session = Depends(get_db)):
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

@app.get("/api/demand", tags=["Buyer"])
def list_buyer_demands(db: Session = Depends(get_db)):
    """Returns all registered buyer demands ordered by newest first."""
    demands = db.query(models.BuyerDemand).order_by(models.BuyerDemand.id.desc()).all()
    return [
        {
            "id": d.id,
            "region": d.region,
            "variety_class": d.variety_class,
            "quantity": d.quantity,
            "status": d.status
        }
        for d in demands
    ]


class ResourceStatusUpdate(BaseModel):
    status: str


@app.patch("/api/resources/plans/{plan_id}/status", tags=["Agrarian"])
def update_resource_plan_status(plan_id: int, payload: ResourceStatusUpdate, db: Session = Depends(get_db)):
    """Allows Agrarian Officers to mark fertilizer/resource plans as Dispatched or Completed."""
    plan = db.query(models.ResourcePlan).filter(models.ResourcePlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Resource plan not found")
    plan.status = payload.status
    db.commit()
    db.refresh(plan)
    return {"id": plan.id, "status": plan.status}


@app.get("/api/agrarian/resource-plans", tags=["Agrarian"])
def list_all_resource_plans(db: Session = Depends(get_db)):
    """Lists individual fertilizer/input tasks across all fields for Agrarian Officers."""
    rows = (
        db.query(models.ResourcePlan, models.Cultivation, models.Field)
        .join(models.Cultivation, models.ResourcePlan.cultivation_id == models.Cultivation.id)
        .join(models.Field, models.Cultivation.field_id == models.Field.id)
        .order_by(models.ResourcePlan.due_date.asc())
        .all()
    )
    return [
        {
            "id": plan.id,
            "field_name": field.name,
            "task_type": plan.task_type,
            "recommended_input": plan.recommended_input,
            "quantity": plan.quantity,
            "unit": plan.unit,
            "due_date": plan.due_date,
            "status": plan.status
        }
        for plan, cult, field in rows
    ]

@app.get("/api/analytics/supply-demand", tags=["Government"])
def get_market_balance(db: Session = Depends(get_db)):
    total_supply = db.query(func.sum(models.HarvestForecast.estimated_quantity)).scalar() or 0.0
    total_demand = db.query(func.sum(models.BuyerDemand.quantity)).scalar() or 0.0
    balance = total_supply - total_demand

    # Regional breakdown
    demands = db.query(models.BuyerDemand).all()
    forecasts = (
        db.query(models.HarvestForecast, models.Field, models.Farm, models.RiceVariety, models.Cultivation)
        .join(models.Cultivation, models.HarvestForecast.cultivation_id == models.Cultivation.id)
        .join(models.Field, models.Cultivation.field_id == models.Field.id)
        .join(models.Farm, models.Field.farm_id == models.Farm.id)
        .join(models.RiceVariety, models.Cultivation.variety_id == models.RiceVariety.id)
        .all()
    )

    regional_map = {}
    for d in demands:
        key = d.region
        regional_map.setdefault(key, {"region": key, "supply_mt": 0.0, "demand_mt": 0.0})
        regional_map[key]["demand_mt"] += float(d.quantity or 0.0)

    for hf, field, farm, variety, cult in forecasts:
        key = farm.region or "Anuradhapura"
        regional_map.setdefault(key, {"region": key, "supply_mt": 0.0, "demand_mt": 0.0})
        regional_map[key]["supply_mt"] += float(hf.estimated_quantity or 0.0)

    regional_breakdown = []
    for reg, vals in regional_map.items():
        net = vals["supply_mt"] - vals["demand_mt"]
        regional_breakdown.append({
            "region": reg,
            "supply_mt": round(vals["supply_mt"], 2),
            "demand_mt": round(vals["demand_mt"], 2),
            "balance_mt": round(net, 2),
            "status": "Shortage" if net < 0 else "Surplus"
        })

    return {
        "total_supply_mt": round(float(total_supply), 2),
        "total_demand_mt": round(float(total_demand), 2),
        "balance_mt": round(float(balance), 2),
        "status": "Critical Shortage" if balance < 0 else "Healthy Surplus",
        "total_cultivations": db.query(models.Cultivation).count(),
        "total_fields_acres": round(float(db.query(func.sum(models.Field.area)).scalar() or 0.0), 2),
        "regional_breakdown": regional_breakdown
    }


@app.get("/api/agrarian/overview", tags=["Agrarian"])
def get_agrarian_overview(db: Session = Depends(get_db)):
    """Returns all registered fields, active cultivations, and fertilizer requirements for Agrarian Officers."""
    rows = (
        db.query(models.Cultivation, models.Field, models.RiceVariety, models.HarvestForecast)
        .join(models.Field, models.Cultivation.field_id == models.Field.id)
        .join(models.RiceVariety, models.Cultivation.variety_id == models.RiceVariety.id)
        .outerjoin(models.HarvestForecast, models.HarvestForecast.cultivation_id == models.Cultivation.id)
        .order_by(models.Cultivation.id.desc())
        .all()
    )

    cultivation_list = []
    for cult, field, variety, forecast in rows:
        cultivation_list.append({
            "cultivation_id": cult.id,
            "field_name": field.name,
            "area_acres": field.area,
            "variety_name": variety.name,
            "planting_date": cult.planting_date,
            "expected_harvest": forecast.estimated_start_date if forecast else cult.expected_harvest_date,
            "expected_yield_mt": forecast.estimated_quantity if forecast else 0.0,
            "status": cult.status
        })

    fertilizer_totals = (
        db.query(models.ResourcePlan.recommended_input, func.sum(models.ResourcePlan.quantity))
        .group_by(models.ResourcePlan.recommended_input)
        .all()
    )

    return {
        "cultivations": cultivation_list,
        "fertilizer_summary": [
            {"input_name": name, "total_kg": round(float(qty or 0.0), 2)}
            for name, qty in fertilizer_totals
        ]
    }

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login", tags=["Users & Auth"])
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates a user and returns their role-based access level."""
    user = db.query(models.User).filter(models.User.username == req.username).first()
    
    # In a production environment, you would use bcrypt to verify hashes here.
    # For this prototype, we match the seeded 'hashed_pw_123' or the raw password.
    if not user or (user.password_hash != req.password and req.password != "hashed_pw_123"):
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    role = db.query(models.Role).filter(models.Role.id == user.role_id).first()
    
    return {
        "user_id": user.id,
        "username": user.username,
        "role": role.name,
        "status": user.status
    }