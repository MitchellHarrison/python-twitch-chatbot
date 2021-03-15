import sqlite3
import requests
import json 
import os
from dotenv import load_dotenv

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


def get_stream_data(channel: str, client_id: str, bearer: str) -> dict:
    url = f"https://api.twitch.tv/helix/streams/?user_login={channel}"
    headers = {
        "client-id" : client_id,
        "authorization": f"Bearer {bearer}"
    }
    response = requests.get(url, headers = headers)
    data = json.loads(response.content)
    return data["data"][0]


def get_follow_data(channel: str, client_id: str, bearer: str, user_id: str, cursor = ""):
    url = f"https://api.twitch.tv/helix/users/follows?to_id={user_id}&first=100&after={cursor}"
    headers = {
        "client-id" : client_id,
        "authorization" : f"Bearer {bearer}"
    }
    response = requests.get(url, headers = headers)
    data = json.loads(response.content)
    # print(json.dumps(data, indent=4))
    return data


bearer = get_bearer(CLIENT_ID, CLIENT_SECRET)
data = get_stream_data(CHANNEL, CLIENT_ID, bearer)
user_id = data["user_id"]
follow_data = get_follow_data(CHANNEL, CLIENT_ID, bearer, user_id)

total_followers = follow_data["total"]
pages_required = (total_followers // 100) + 1

cursor = ""
followers = []

for _ in range(pages_required):
    follow_data = get_follow_data(CHANNEL, CLIENT_ID, bearer, user_id, cursor)
    followers.extend([f["from_name"] for f in follow_data["data"]])
    
    # last page has no cursor
    try:
        cursor = follow_data["pagination"]["cursor"]
    except KeyError:
        pass

print(followers)
print(len(followers))
