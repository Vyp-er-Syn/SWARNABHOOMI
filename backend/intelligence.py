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
    
    # Save the forecast to the database
    forecast = models.HarvestForecast(
        cultivation_id=cultivation.id,
        estimated_start_date=start_date,
        estimated_end_date=end_date,
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