import requests 
import os 
import json
from database import Base, Session, engine
from sqlalchemy import select, delete, insert
from models import Tokens
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
        self.callback_address = os.getenv("CALLBACK_ADDRESS")

        self.scopes = [
            "bits:read",
            "channel:read:redemptions",
            "channel:read:subscriptions"
        ]

        # these are pre-defined
        self.irc_port = 6667
        self.irc_server = "irc.twitch.tv"

        # start with new tokens
        self.refresh_bearer()
        self.refresh_app_access()

        self.user_id = self.get_user_id()
        self.app_access = self.get_app_access()


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


    def refresh_app_access(self) -> None:
        # delete old app access token
        engine.execute(
            delete(Tokens)
            .where(Tokens.name=="App_Access")
        )

        # get new app access token
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(url, params=params)
        token = response.json()["access_token"]

        # write new token to db
        entry = {
            "name": "App_Access",
            "token": token
        }
        engine.execute(
            insert(Tokens)
            .values(entry)
        )
        

    # read app access token from db
    def get_app_access(self):
        result = engine.execute(
            select(Tokens.token)
            .where(Tokens.name=="App_Access")
        ).fetchone()
        token = result[0]
        return token


    # TODO: use longer sql statement to update if exists
    def set_user_access(self, token:str) -> None:
        # delete old token
        engine.execute(
            delete(Tokens)
            .where(Tokens.name=="User_Access")
        )

        # set new token
        entry = {
            "name": "User_Access",
            "token": token
        }
        engine.execute(
            insert(Tokens)
            .values(entry)
        )


    def get_user_access(self) -> str:
        result = engine.execute(
            select(Tokens.token)
            .where(Tokens.name=="User_Access")
        ).fetchone()
        token = result[0]
        return token


    # TODO: use longer sql statement to update if exists
    def set_refresh_token(self, token:str) -> None:
        # del old token
        engine.execute(
            delete(Tokens)
            .where(Tokens.name=="Refresh")
        )

        # write new token
        entry = {
            "name": "Refresh",
            "token": token
        }
        engine.execute(
            insert(Tokens)
            .values(entry)
        )


    def get_refresh_token(self) -> str:
        result = engine.execute(
            select(Tokens.token)
            .where(Tokens.name=="Refresh")
        ).fetchone()
        token = result[0]
        return token

env = Environment()

