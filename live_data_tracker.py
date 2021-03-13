import sqlite3
import json 
import requests 
import os  
import time
import sched
from dotenv import load_dotenv
from datetime import datetime

load_dotenv("./credentials.env")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
OAUTH_TOKEN = os.getenv("OAUTH_TOKEN")
CHANNEL = os.getenv("CHANNEL")

conn = sqlite3.connect("data.db")
cursor = conn.cursor()
with conn:
    cursor.execute("""CREATE TABLE IF NOT EXISTS live_data 
                        (time text, 
                        user text, 
                        language text,
                        game_name text,
                        viewer_count integer,
                        title text,
                        tags text);""")   

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


def get_tags(channel: str, client_id: str, bearer: str, broadcaster_id: str) -> list:
    url = f"https://api.twitch.tv/helix/streams/tags?broadcaster_id={broadcaster_id}"
    headers = {
        "client-id": client_id,
        "authorization": f"Bearer {bearer}"
    }
    response = requests.get(url, headers=headers)
    tags_data = json.loads(response.content)["data"]
    tags = []
    for t in tags_data:
        tags.append(t["localization_names"]["en-us"])
    return tags


def write_live_data(entry):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    with conn:
        cursor.execute(f"""INSERT INTO live_data 
                        (time, user, language,game_name, viewer_count, title, tags) 
                        VALUES 
                        (:time, :user, :language, :game_name, :viewer_count, :title, :tags)""", entry)
    conn.commit()
    cursor.close()
    conn.close()



bearer = get_bearer(CLIENT_ID, CLIENT_SECRET)
while True:
    try:
        stream_data = get_stream_data(CHANNEL, CLIENT_ID, bearer) 
        is_live = stream_data["type"] == "live"
        broadcaster_id = stream_data["user_id"]
        current_min = datetime.now().minute
        print(current_min)

    except IndexError:
        print("Broadcaster is not currently live")
        time.sleep(60)        

while is_live:
    if current_min != datetime.now().minute:
        current_min = datetime.now().minute
        username = stream_data["user_name"]
        language = stream_data["language"]
        game_name = stream_data["game_name"]
        viewer_count = stream_data["viewer_count"]
        title = stream_data["title"]
        tags_list = get_tags(CHANNEL, CLIENT_ID, bearer, broadcaster_id)

        live_entry = {
            "time" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user" : username,
            "language" : language,
            "game_name" : game_name,
            "viewer_count" : viewer_count,
            "title" : title,
            "tags" : str(tags_list)
        }
        write_live_data(live_entry)
        print("entry made!")
