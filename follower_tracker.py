from environment import env
from sqlalchemy import select, insert
from database import Base, engine
from models import Followers

Base.metadata.create_all(bind=engine)

def get_follower_count(env=env) -> int:
    pass


# reconstuct follower table
def fill_follower_table(env=env) -> None:
    pass

