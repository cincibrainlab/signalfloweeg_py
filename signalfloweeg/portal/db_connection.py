from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from sqlalchemy_utils.functions import drop_database, create_database
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
            from sqlalchemy import text
            session.execute(text("SELECT 1"))
            return True
    except SQLAlchemyError as e:
        logging.error(f"Database connection error: {e}")
        return False
    
def delete_database():
    drop_database(db_url)
    create_database(db_url)


#delete_database()