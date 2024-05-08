from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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
