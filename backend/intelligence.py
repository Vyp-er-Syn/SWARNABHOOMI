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