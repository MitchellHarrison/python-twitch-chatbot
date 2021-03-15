import os
import sqlite3
from dotenv import load_dotenv
from bot import Bot

load_dotenv("./credentials.env")
CLIENT_ID = os.getenv("CLIENT_ID")
OAUTH_TOKEN = os.getenv("OAUTH_TOKEN")
BOT_NAME = os.getenv("BOT_NAME")
CHANNEL = os.getenv("CHANNEL")
SERVER = "irc.twitch.tv"
PORT = 6667


# check for missing .db file or missing tables, and create them
def db_setup():
    # if "data.db" doesn't exist, connect() will create it
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    with conn:
        cursor.execute("CREATE TABLE IF NOT EXISTS command_use (time text, user text, command text, is_custom number);")
        cursor.execute("CREATE TABLE IF NOT EXISTS chat_messages (time text, user text);")
        cursor.execute("CREATE TABLE IF NOT EXISTS text_commands (command text, message text);")
        cursor.execute("CREATE TABLE IF NOT EXISTS false_commands (time text, user text, command text);")
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


def main():
    db_setup()
    text_commands = get_text_commands()
    bot = Bot(SERVER, PORT, OAUTH_TOKEN, BOT_NAME, CHANNEL, text_commands)
    bot.connect_to_channel()


if __name__ == "__main__":
    main()
