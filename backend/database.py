import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Fetch database URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://swarna_admin:secure_password_here@db:5432/swarnabhoomi_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Append to the bottom of backend/database.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()