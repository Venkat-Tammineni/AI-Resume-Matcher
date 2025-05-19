from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Fix the connection string format
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:Venkat%409346@localhost/resumedb"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to use in endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
