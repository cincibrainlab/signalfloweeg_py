from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging


db_url = "postgresql://sfportal:sfportal@localhost:3002/sfportal"


@contextmanager
def get_session():
    # Now connect to the new or existing database
    engine = create_engine(db_url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_db_url():
    return db_url


def get_engine():
    # Now connect to the new or existing database
    engine = create_engine(db_url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        return engine
    finally:
        session.close()

def is_database_connected():
    """
    Check if the database is connected.

    Returns:
        bool: True if the database is connected, False otherwise.
    """
    try:
        with get_session() as session:
            session.execute("SELECT 1")
            return True
    except SQLAlchemyError as e:
        logging.error(f"Database connection error: {e}")
        return False