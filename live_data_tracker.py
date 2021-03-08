import sqlite3
import json 
import requests 
import os  
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv("./credentials.env")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
OAUTH_TOKEN = os.getenv("OAUTH_TOKEN")
CHANNEL = os.getenv("CHANNEL")

def get_bearer(client_id: str, client_secret: str) -> str:
    url = f"https://id.twitch.tv/oauth2/token"
    params = {
        "client_id" : client_id,
        "client_secret" : client_secret,
        "grant_type" : "client_credentials"
    } 
    response = requests.post(url, params = params)
    data = json.loads(response.content)
    bearer = data["access_token"]
    return bearer


def get_live_status(channel: str, client_id: str, bearer: str) -> bool:
    url = f"https://api.twitch.tv/helix/search/channels?query={channel}" 
    headers = {
        "client-id" : client_id,
        "authorization" : f"Bearer {bearer}"
    }
    response = requests.get(url, headers = headers)
    data = json.loads(response.content)
    is_live = data["data"][0]["is_live"]
    return is_live


def get_channel_id(channel: str, client_id: str, bearer: str) -> str:
    url = f"https://api.twitch.tv/helix/search/channels?query={channel}" 
    headers = {
        "client-id" : client_id,
        "authorization" : f"Bearer {bearer}"
    }
    response = requests.get(url, headers = headers)
    data = json.loads(response.content)
    channel_id = data["data"][0]["id"]
    return channel_id


bearer = get_bearer(CLIENT_ID, CLIENT_SECRET)
is_live = get_live_status(CHANNEL, CLIENT_ID, bearer)
channel_id = get_channel_id(CHANNEL, CLIENT_ID, bearer)
