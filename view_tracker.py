import requests
import json
from sqlalchemy import insert, select
from database import engine
from models import Viewership
from environment import env

# get stream data from Twitch
def get_stream_data(env=env) -> dict:
    url = "https://api.twitch.tv/helix/streams"
    headers = {
        "Authorization": f"Bearer {env.get_bearer()}",
        "Client-Id": env.client_id
    }
    params = {"user_id": env.user_id}
    response = requests.get(url=url, headers=headers, params=params).json()
    data = response["data"][0]
    return data


# write stream data to db
def write_stream_data(entry: dict) -> None:
    engine.execute(
        insert(Viewership)
        .values(entry)
    )
    result = engine.execute(
        select(Viewership)
    ).fetchall()


# once per minute
def main():
    # get data
    data = get_stream_data()
    datapoints = [
        "title",
        "game_id",
        "game_name",
        "viewer_count"
    ]
    entry = {k:data[k] for k in datapoints}
    entry["stream_id"] = data["id"]
    
    # write data
    write_stream_data(entry)


if __name__ == "__main__":
    main()

