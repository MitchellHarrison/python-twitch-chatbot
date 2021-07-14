import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError
load_dotenv("../credentials.env")

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DB_BASE_URL = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@localhost:5432/"
DB_FINAL_URL = DB_BASE_URL + DB_NAME 

base_engine = create_engine(DB_BASE_URL)

# create database if it doesn't exist
try:
    conn = base_engine.connect()

    # commit empty statement as a sqlalchemy workaround
    conn.execute("commit")

    # create database
    conn.execute(f"CREATE DATABASE {DB_NAME};")
    conn.close()
    
except ProgrammingError:
    pass

# final engine, Base, and Session used in other scripts
engine = create_engine(DB_FINAL_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

