from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError

DB_BASE_URL = "postgresql+psycopg2://postgres:password@localhost:5432/"
DB_NAME = "stream_data"
DB_FINAL_URL = DB_BASE_URL + DB_NAME

base_engine = create_engine(DB_BASE_URL)

try:
    conn = base_engine.connect()
    conn.execute("commit")
    conn.execute(f"CREATE DATABASE {DB_NAME};")
    conn.close()
except ProgrammingError:
    pass

engine = create_engine(DB_FINAL_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

