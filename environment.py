from database import Base, Session, engine
from sqlalchemy import select, delete, insert
from models import Tokens
import requests 
import os 
import json
from dotenv import load_dotenv
load_dotenv("./credentials.env")

Base.metadata.create_all(bind=engine)
session = Session()

class Environment():
    def __init__(self):
        # get creds from env file
        self.channel = os.getenv("CHANNEL")
        self.bot_name = os.getenv("BOT_NAME")
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.oauth = os.getenv("OAUTH_TOKEN")

        # these are pre-defined
        self.irc_port = 6667
        self.irc_server = "irc.twitch.tv"

        self.user_id = self.get_user_id()

    
    # get new bearer token
    def refresh_bearer(self) -> None:
        # delete existing bearer
        engine.execute(
            delete(Tokens)
            .where(Tokens.name == "Bearer")
        )

        # get new bearer from Twitch
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id" : self.client_id,
            "client_secret" : self.client_secret,
            "grant_type" : "client_credentials"
            }
        response = requests.post(url, params = params, timeout=3)
        data = json.loads(response.content)
        bearer = data["access_token"]

        # write new bearer to database
        entry = {
            "name": "Bearer",
            "token": bearer
        }
        engine.execute(
            insert(Tokens)
            .values(entry)
        )

    
    # get bearer from database
    def get_bearer(self) -> str:
        result = engine.execute(
            select(Tokens.token)
            .where(Tokens.name == "Bearer")
        ).fetchone()

        # return bearer from result
        bearer = result[0]
        return bearer

    def get_user_id(self) -> str:
        url = f"https://api.twitch.tv/helix/users?login={self.channel}"
        headers = {
            "client-id": self.client_id,
            "authorization": f"Bearer {self.get_bearer()}"
            }
        response = requests.get(url, headers = headers)
        data = json.loads(response.content)
        user_id = data["data"][0]["id"]
        return user_id

env = Environment()
env.get_bearer()

