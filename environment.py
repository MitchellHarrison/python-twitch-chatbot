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

    
    def get_bearer(self) -> str:
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id" : self.client_id,
            "client_secret" : self.client_secret,
            "grant_type" : "client_credentials"
        } 
        response = requests.post(url, params = params)
        data = json.loads(response.content)
        bearer = data["access_token"]
        return bearer

    
    def authorize(self) -> str:
        url = "https://id.twitch.tv/oauth2/authorize"
