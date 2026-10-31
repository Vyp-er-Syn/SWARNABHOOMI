from datetime import timedelta
from sqlalchemy.orm import Session
import models

def calculate_harvest_window(db: Session, cultivation_id: int):
    """
    Phase 1 Rule: 
    HarvestStart = PlantingDate + DurationMinDays
    HarvestEnd = PlantingDate + DurationMaxDays
    """
    cultivation = db.query(models.Cultivation).filter(models.Cultivation.id == cultivation_id).first()
    if not cultivation:
        return None
        
    variety = db.query(models.RiceVariety).filter(models.RiceVariety.id == cultivation.variety_id).first()
    
    start_date = cultivation.planting_date + timedelta(days=variety.duration_min_days)
    end_date = cultivation.planting_date + timedelta(days=variety.duration_max_days)
    
    # Calculate expected production (Area * Yield Class / Base rate)
    # For MVP, assuming variety.yield_class contains a string like "4.5" MT per Acre
    try:
        expected_yield_rate = float(variety.yield_class)
    except (ValueError, TypeError):
        expected_yield_rate = 2.0 # Fallback default 2 MT/Acre
        
    estimated_production_mt = cultivation.area * expected_yield_rate
    
    # Save the forecast to the database with the populated estimated_quantity
    forecast = models.HarvestForecast(
        cultivation_id=cultivation.id,
        estimated_start_date=start_date,
        estimated_end_date=end_date,
        estimated_quantity=estimated_production_mt,
        confidence="Rule-Based"
    )
    db.add(forecast)
    db.commit()
    db.refresh(forecast)
    
    return forecast

def generate_resource_plans(db: Session, cultivation_id: int):
    """
    Calculates required resources based on field area and variety rules.
    """
    cultivation = db.query(models.Cultivation).filter(models.Cultivation.id == cultivation_id).first()
    if not cultivation:
        return []

    plans = []
    
    # 1. Calculate Seed Requirement
    seed_rules = db.query(models.SeedRule).filter(models.SeedRule.variety_id == cultivation.variety_id).all()
    for rule in seed_rules:
        # Expected quantity = field area * configured rate per area
        qty = cultivation.area * rule.rate_per_area
        plan = models.ResourcePlan(
            cultivation_id=cultivation.id,
            resource_type="Seed",
            stage="Crop Establishment",
            quantity=qty,
            due_date=cultivation.planting_date, # Seed is needed at planting
            status="Planned"
        )
        db.add(plan)
        plans.append(plan)

    # 2. Calculate Fertilizer Schedule
    fert_rules = db.query(models.FertilizerRule).filter(models.FertilizerRule.variety_id == cultivation.variety_id).all()
    for rule in fert_rules:
        qty = cultivation.area * rule.rate_per_area
        # Shift template dates from planting date based on crop stage rule
        due_date = cultivation.planting_date + timedelta(days=rule.day_from_planting)
        
        plan = models.ResourcePlan(
            cultivation_id=cultivation.id,
            resource_type="Fertilizer",
            stage=f"{rule.stage_name} ({rule.nutrient})",
            quantity=qty,
            due_date=due_date,
            status="Planned"
        )
        db.add(plan)
        plans.append(plan)

    db.commit()
    return plans

# Append to backend/intelligence.py
from sqlalchemy import func

def calculate_supply_demand_balance(db: Session, season_id: int, region: str, variety_class: str):
    """
    Compares verified buyer demand against expected harvest supply.
    Returns SHORTAGE, BALANCED, or HIGH SUPPLY[cite: 19].
    """
    # 1. Aggregate Total Demand for this segment
    total_demand = db.query(func.sum(models.BuyerDemand.quantity)).filter(
        models.BuyerDemand.season_id == season_id,
        models.BuyerDemand.region == region,
        models.BuyerDemand.variety_class == variety_class
    ).scalar() or 0.0

    # 2. Aggregate Expected Supply
    # Joins Cultivation to HarvestForecast to sum expected yield
    expected_supply = db.query(func.sum(models.HarvestForecast.estimated_quantity)).join(
        models.Cultivation, models.HarvestForecast.cultivation_id == models.Cultivation.id
    ).join(
        models.RiceVariety, models.Cultivation.variety_id == models.RiceVariety.id
    ).join(
        models.Field, models.Cultivation.field_id == models.Field.id
    ).join(
        models.Farm, models.Field.farm_id == models.Farm.id
    ).filter(
        models.Cultivation.season_id == season_id,
        models.RiceVariety.maturity_class == variety_class,
        models.Farm.location.ilike(f"%{region}%")
    ).scalar() or 0.0

    # 3. Determine Market Balance Status
    status = "BALANCED"
    if expected_supply < total_demand * 0.9:
        status = "SHORTAGE"
    elif expected_supply > total_demand * 1.1:
        status = "HIGH SUPPLY"

    return {
        "region": region,
        "variety_class": variety_class,
        "total_demand_mt": total_demand,
        "expected_supply_mt": expected_supply,
        "balance_status": status
    }

# Append to backend/intelligence.py
from sqlalchemy import func

def calculate_supply_demand_balance(db: Session, season_id: int, region: str, variety_class: str):
    """
    Compares verified buyer demand against expected harvest supply.
    Returns SHORTAGE, BALANCED, or HIGH SUPPLY[cite: 19].
    """
    # 1. Aggregate Total Demand for this segment
    total_demand = db.query(func.sum(models.BuyerDemand.quantity)).filter(
        models.BuyerDemand.season_id == season_id,
        models.BuyerDemand.region == region,
        models.BuyerDemand.variety_class == variety_class
    ).scalar() or 0.0

    # 2. Aggregate Expected Supply
    # Joins Cultivation to HarvestForecast to sum expected yield
    expected_supply = db.query(func.sum(models.HarvestForecast.estimated_quantity)).join(
        models.Cultivation, models.HarvestForecast.cultivation_id == models.Cultivation.id
    ).join(
        models.RiceVariety, models.Cultivation.variety_id == models.RiceVariety.id
    ).join(
        models.Field, models.Cultivation.field_id == models.Field.id
    ).join(
        models.Farm, models.Field.farm_id == models.Farm.id
    ).filter(
        models.Cultivation.season_id == season_id,
        models.RiceVariety.maturity_class == variety_class,
        models.Farm.location.ilike(f"%{region}%")
    ).scalar() or 0.0

    # 3. Determine Market Balance Status
    status = "BALANCED"
    if expected_supply < total_demand * 0.9:
        status = "SHORTAGE"
    elif expected_supply > total_demand * 1.1:
        status = "HIGH SUPPLY"

    return {
        "region": region,
        "variety_class": variety_class,
        "total_demand_mt": total_demand,
        "expected_supply_mt": expected_supply,
        "balance_status": status
    }