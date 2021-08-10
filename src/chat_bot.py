from sqlalchemy import select, update, insert
from bot import Bot
from environment import env
from datetime import datetime
from sqlalchemy import select, insert
from database import Base, Session, engine
from models import TextCommands, BotTime 


def main():
    # create all tables
    Base.metadata.create_all(bind=engine)

    # log bot startup time
    engine.execute(insert(BotTime))

    bot = Bot()
    bot.connect_to_channel()

    # loop forever
    bot.check_for_messages()


if __name__ == "__main__":
    main()

