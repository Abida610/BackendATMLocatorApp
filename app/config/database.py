from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base



engine = create_engine( "postgresql+psycopg2://postgres:maryem222@192.168.208.1:5432/atm_app?options=-c%20client_encoding%3Dutf8"
)
SessionLocal = sessionmaker( bind=engine,autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
