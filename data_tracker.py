import json 
import requests 
import os  
import time
from dotenv import load_dotenv
from datetime import datetime
from environment import Environment
from sqlalchemy import insert
from database import engine, Base, Session
from models import Followers


def db_setup(channel: str, client_id: str, bearer: str, user_id: int, follow_pages_required = 0):
    follow_data = get_all_followers(
        channel,
        client_id,
        bearer,
        user_id,
        follow_pages_required
    )

    # write to table
    for follower in follow_data:
        entry = {
            "username" : follower["from_login"],
            "user_id" : follower["from_id"],
            "time" : datetime.strptime(follower["followed_at"], "%Y-%m-%dT%H:%M:%SZ")
        }
        engine.execute(
            insert(Followers)
            .values(entry)
        )


def get_stream_data(channel: str, client_id: str, bearer: str) -> dict:
    url = f"https://api.twitch.tv/helix/streams/?user_login={channel}"
    headers = {
        "client-id" : client_id,
        "authorization": f"Bearer {bearer}"
    }
    response = requests.get(url, headers = headers)
    data = json.loads(response.content)
    return data["data"][0]


def get_tags(channel: str, client_id: str, bearer: str, user_id: str) -> list:
    url = f"https://api.twitch.tv/helix/streams/tags?user_id={user_id}"
    headers = {
        "client_id": client_id,
        "authorization": f"Bearer {bearer}"
    }
    response = requests.get(url, headers=headers)
    tags_data = json.loads(response.content)["data"]
    tags = []
    for t in tags_data:
        tags.append(t["localization_names"]["en-us"])
    return tags


def get_follow_data(channel: str, client_id: str, bearer: str, user_id: str, cursor = "") -> dict:
    url = f"https://api.twitch.tv/helix/users/follows?to_id={user_id}&first=100&after={cursor}"
    headers = {
        "client-id" : client_id,
        "authorization" : f"Bearer {bearer}"
    }
    response = requests.get(url, headers = headers)
    data = json.loads(response.content)
    return data


def get_all_followers(channel: str, client_id: str, bearer: str, user_id: str,  pages: int, cursor = "") -> dict:
    cursor = ""
    followers = []
    for _ in range(pages):
        follow_data = get_follow_data(channel, client_id, bearer, user_id, cursor)
        followers.extend(follow_data["data"])
        
        # last page has no cursor
        try:
            cursor = follow_data["pagination"]["cursor"]
        except KeyError:
            pass
    return followers


# TODO:
def get_subscribers(channel: str, client_id: str, bearer: str, user_id: str, cursor = "") -> dict:
    url = f"https://api.twitch.tv/helix/subscriptions?broadcaster_id={user_id}"
    headers = {
        "client-id" : client_id,
        "authorization" : f"Bearer {bearer}"
    }
    response = requests.get(url, headers = headers)
    data = json.loads(response.content)
    print(json.dumps(data, indent=4))


#TODO
def get_subscriber_list() -> list:
    pass


def main():
    Base.metadata.create_all(bind=engine)
    session = Session()
    environment = Environment()
    channel = environment.channel
    client_id = environment.client_id
    bearer = environment.bearer
    user_id = environment.user_id
    current_min = datetime.now().minute

    follow_data = get_follow_data(channel, client_id, bearer, user_id)
    total_followers = follow_data["total"]
    follow_pages_required = (total_followers // 100) + 1

    # build database tables where necessary
    db_setup(
        channel, 
        client_id, 
        bearer, 
        user_id, 
        follow_pages_required
    )

    stream_data = get_stream_data(channel, client_id, bearer)
    is_live = stream_data["type"] == "live"

    while True:
        try:
            stream_data = get_stream_data(channel, client_id, bearer) 
            is_live = stream_data["type"] == "live"
            user_id = stream_data["user_id"]
            current_min = datetime.now().minute
            break
        
        except IndexError:
            print("Broadcaster is not currently live")
            time.sleep(5)        

    while is_live:
        if current_min != datetime.now().minute:
            current_min = datetime.now().minute
            username = stream_data["user_name"]
            language = stream_data["language"]
            game_name = stream_data["game_name"]
            viewer_count = stream_data["viewer_count"]
            title = stream_data["title"]
            tags_list = get_tags(channel, client_id, bearer, user_id)

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
            print(f"Live Data entry made! - {datetime.now()}")

            stream_data = get_stream_data(channel, client_id, bearer) 
            is_live = stream_data["type"] == "live"


if __name__ == "__main__":
    main()
