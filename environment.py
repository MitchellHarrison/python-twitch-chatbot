import requests 
import os 
import json
from dotenv import load_dotenv
load_dotenv("./credentials.env")

class Environment():
    def __init__(self):
        self.channel = os.getenv("CHANNEL")
        self.bot_name = os.getenv("BOT_NAME")
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.oauth = os.getenv("OAUTH_TOKEN")
        self.irc_port = 6667
        self.irc_server = "irc.twitch.tv"
        self.bearer = self.get_bearer()
        self.user_id = self.get_user_id()

    
    def get_bearer(self) -> str:
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id" : self.client_id,
            "client_secret" : self.client_secret,
            "grant_type" : "client_credentials"
            }
        response = requests.post(url, params = params, timeout=3)
        data = json.loads(response.content)
        bearer = data["access_token"]
        return bearer


    def get_user_id(self) -> str:
        url = f"https://api.twitch.tv/helix/users?login={self.channel}"
        headers = {
            "client-id": self.client_id,
            "authorization": f"Bearer {self.bearer}"
            }
        response = requests.get(url, headers = headers)
        data = json.loads(response.content)
        user_id = data["data"][0]["id"]
        return user_id
