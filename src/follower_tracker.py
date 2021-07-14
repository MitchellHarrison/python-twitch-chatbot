import requests
from datetime import datetime, timedelta
from environment import env
from sqlalchemy import select, insert, func, delete, update
from database import Base, engine
from models import Followers

Base.metadata.create_all(bind=engine)

FOLLOW_URL = "https://api.twitch.tv/helix/users/follows"
FOLLOW_HEADERS = {
    "Authorization": f"Bearer {env.app_access}",
    "Client-Id": env.client_id
}
 
def get_follower_count(env=env) -> int:
    # api response
    response = requests.get(
        url=FOLLOW_URL, 
        headers=FOLLOW_HEADERS, 
        params={"to_id":env.user_id}
    ).json()
    follow_count = response["total"]
    return follow_count


# get followers from database
def get_db_followers() -> int:
    # count the number of followers currently in the database
    followers = engine.execute(
        select([func.count()]).select_from(Followers)
    ).fetchone()[0]
    
    return followers

# reconstuct follower table
def refresh_follow_table(env=env) -> None:
    params = {
        "to_id": env.user_id,
        "first": 100 # max allowed by twitch
    }
    response = requests.get(
        url=FOLLOW_URL, 
        headers=FOLLOW_HEADERS, 
        params=params
    ).json()

    # run until end of follower list
    while True:
        data = response["data"]
        params["after"] = cursor
        
        try:
            cursor = response["pagination"]["cursor"]
        except KeyError:
            pass

        # check every follower
        for follower in data:
            entry = {
                "user_id": follower["from_id"],
                "follow_time": follower["followed_at"],
                "username": follower["from_name"]
            }
            # if follower in table, update last_seen
            try:
                update_entry = {
                    "last_seen": datetime.now(),
                    "username": entry["username"]
                }
                engine.execute(
                    update(Followers)
                    .where(Followers.user_id == entry["user_id"])
                    .values(update_entry)
                )

            # if follower not in database
            except Exception as e: 
                print(e)
                # write new follower
                engine.execute(
                    insert(Followers)
                    .values(entry)
                )

        # stop running on last page
        if not response["pagination"]:
            break
            
        # make new request with new cursor
        response = requests.get(
            url=FOLLOW_URL, 
            headers=FOLLOW_HEADERS, 
            params=params
        ).json()


    # delete unfollows
    # remove rows with last_seen values > 12 hours
    engine.execute(
        delete(Followers)
        .where(Followers.last_seen < datetime.now() - timedelta(hours=12))
    )


def main():
    followers = get_follower_count()
    db_followers = get_db_followers()

    if followers != db_followers:
        refresh_follow_table()


if __name__ == "__main__":
    main()

