"""
Database setup using SQLAlchemy.
This creates the engine, session factory, and base class for models.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create SQLAlchemy engine
# echo=False means we won't log all SQL queries (set to True for debugging)
engine = create_engine(settings.DATABASE_URL, echo=False)

# SessionLocal is a factory for creating database sessions
# autocommit=False: we control when to commit
# autoflush=False: we control when to flush changes to DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    Dependency function that yields a database session.
    Usage: def endpoint(db: Session = Depends(get_db))
    The session is automatically closed after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
