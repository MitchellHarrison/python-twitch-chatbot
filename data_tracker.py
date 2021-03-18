import sqlite3
import json 
import requests 
import os  
import time
import sched
from dotenv import load_dotenv
from datetime import datetime
from environment import Environment

def db_setup(channel: str, client_id: str, bearer: str, user_id: int, follow_pages_required = 0):
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
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS stream_summary
                            (start_time text,
                            end_time text,
                            stream_length text,
                            title text,
                            category text, 
                            new_followers number,
                            new_t1_subscribers number,
                            new_t2_subscribers number,
                            new_t3_subscribers number,
                            new_prime_subscribers number,
                            average_viewers real,
                            unique_chatters number,
                            chat_messages number,
                            chat_commands number,
                            peak_viewership number,
                            number_of_raids number,
                            total_raiders number
                            );""")  


        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        if "followers" not in tables:
            # create table
            cursor.execute("""CREATE TABLE IF NOT EXISTS followers
                                (username text,
                                id text,
                                time text);""")
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
                    "id" : follower["from_id"],
                    "time" : follower["followed_at"]
                }
                cursor.execute("""INSERT INTO followers
                                    (username, id, time)
                                    VALUES
                                    (:username, :id, :time)""", entry)        
    cursor.close()
    conn.close()    


def get_stream_data(channel: str, client_id: str, bearer: str) -> dict:
    print(bearer)
    print(client_id)
    url = f"https://api.twitch.tv/helix/streams/?user_login={channel}"
    headers = {
        "client-id" : client_id,
        "authorization": f"Bearer {bearer}"
    }
    response = requests.get(url, headers = headers)
    data = json.loads(response.content)
    print(json.dumps(data, indent = 4))
    return data["data"][0]


def get_tags(channel: str, client_id: str, bearer: str, user_id: str) -> list:
    url = f"https://api.twitch.tv/helix/streams/tags?user_id={user_id}"
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


def get_subscriber_list() -> list:
    pass


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


def main():
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
