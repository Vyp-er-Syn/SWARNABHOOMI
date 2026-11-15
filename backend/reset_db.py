from sqlalchemy import text
from database import engine
import models

print("Dropping all old tables with CASCADE...")

with engine.connect() as conn:
    # 1. Drop legacy tables that are no longer in models.py
    conn.execute(text("DROP TABLE IF EXISTS actual_harvests CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
    
    # 2. Drop all current model tables with CASCADE to bypass foreign key locks
    for table in reversed(models.Base.metadata.sorted_tables):
        conn.execute(text(f'DROP TABLE IF EXISTS "{table.name}" CASCADE;'))
        
    conn.commit()

print("Recreating fresh tables from models.py...")
models.Base.metadata.create_all(bind=engine)

print("Database reset complete! Now start Uvicorn.")