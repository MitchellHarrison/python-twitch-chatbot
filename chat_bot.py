import os
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

def main():
    bot = Bot(SERVER, PORT, OAUTH_TOKEN, BOT_NAME, CHANNEL)
    bot.connect_to_channel()


if __name__ == "__main__":
    main()
