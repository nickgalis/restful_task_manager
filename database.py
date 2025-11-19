"""
Database connection and initialization module.

This module handles database setup, connection management, and initialization.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base
import os

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'task_manager.db')
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

# Create engine with echo for debugging (set to False in production)
engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False},  # Needed for SQLite
    echo=False
)

# Create session factory
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def init_db():
    """
    Initialize the database by creating all tables.
    
    This function creates all tables defined in the models module
    if they don't already exist.
    """
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


def get_db():
    """
    Get a database session.
    
    This is a dependency function that can be used to get a database session
    for handling requests. It ensures the session is properly closed after use.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def drop_all_tables():
    """
    Drop all tables from the database.
    
    WARNING: This will delete all data! Use with caution.
    """
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped successfully!")


def reset_db():
    """
    Reset the database by dropping all tables and recreating them.
    
    WARNING: This will delete all data! Use with caution.
    """
    drop_all_tables()
    init_db()
    print("Database reset successfully!")


if __name__ == '__main__':
    # Initialize database when run directly
    init_db()
