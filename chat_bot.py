from sqlalchemy import select, update, insert
from bot import Bot
from environment import env
from datetime import datetime
from sqlalchemy import select, insert
from database import Base, Session, engine
from models import TextCommands, BotTime 


def get_text_commands() -> dict:
    command_rows = engine.execute(select(TextCommands.command, TextCommands.message))
    text_commands = {k:v for k,v in [e for e in command_rows]}
    return text_commands


def main():
    # create all tables
    Base.metadata.create_all(bind=engine)

    # log bot startup time
    engine.execute(insert(BotTime))

    text_commands = get_text_commands()
    bot = Bot(
        env.irc_server,
        env.irc_port,
        env.oauth,
        env.bot_name,
        env.channel,
        env.user_id,
        env.client_id,
        text_commands
    )
    bot.connect_to_channel()


if __name__ == "__main__":
    main()

