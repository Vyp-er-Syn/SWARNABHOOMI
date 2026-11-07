import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Fetch database URL from environment variables, fallback to localhost for local testing
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://swarna_admin:secure_password_here@localhost:5432/swarnabhoomi_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()