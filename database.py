from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = "sqlite:///./data.db"

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

