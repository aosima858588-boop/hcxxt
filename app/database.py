import os
from sqlmodel import SQLModel, create_engine, Session

# Get database URL from environment variable, default to sqlite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session
