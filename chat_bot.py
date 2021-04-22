import sqlite3
from bot import Bot
from environment import Environment
from datetime import datetime

# check for missing .db file or missing tables, and create them
def db_setup():
    # if "data.db" doesn't exist, connect() will create it
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    with conn:
        cursor.execute("CREATE TABLE IF NOT EXISTS command_use (time text, user text, command text, is_custom number);")
        cursor.execute("CREATE TABLE IF NOT EXISTS chat_messages (time text, user text, message text);")
        cursor.execute("CREATE TABLE IF NOT EXISTS text_commands (command text, message text);")
        cursor.execute("CREATE TABLE IF NOT EXISTS false_commands (time text, user text, command text);")
        cursor.execute("CREATE TABLE IF NOT EXISTS bot_logs (time text);")
    cursor.close()
    conn.close()


def get_text_commands() -> dict:
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    with conn:
        commands = {k:v for k,v in [e for e in cursor.execute("SELECT * FROM text_commands;")]}
    cursor.close()
    conn.close()
    return commands

def bot_startup():
    now = datetime.now()
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    with conn:
        commands = {cursor.execute("UPDATE bot_logs SET time=(now)")};
    cursor.close()
    con.close()
    return commands

def main():
    db_setup()
    bot_startup()
    text_commands = get_text_commands()
    environment = Environment()
    bot = Bot(
        environment.irc_server,
        environment.irc_port,
        environment.oauth,
        environment.bot_name,
        environment.channel,
        environment.user_id,
        environment.client_id,
        text_commands
    )
    bot.connect_to_channel()


if __name__ == "__main__":
    main()

