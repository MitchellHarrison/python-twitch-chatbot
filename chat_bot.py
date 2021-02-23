import os
import sqlite3
import Command
from dotenv import load_dotenv
from Bot import Bot

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
        cursor.execute("CREATE TABLE IF NOT EXISTS command_use (time text, user text, command text);")
        cursor.execute("CREATE TABLE IF NOT EXISTS chat_messages (time text, user text);")
    cursor.close()
    conn.close()


def main():
    db_setup()
    bot = Bot(SERVER, PORT, OAUTH_TOKEN, BOT_NAME, CHANNEL)
    bot.connect_to_channel()


if __name__ == "__main__":
    main()
