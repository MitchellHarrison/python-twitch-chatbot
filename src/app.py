import os
import json
import requests
import hashlib
import webbrowser
import urllib.parse
from environment import env, Environment
from flask import Flask, Response
from flask import request as flask_request
from database import engine, Base
from sqlalchemy import insert, update
from models import Subscriptions

SUB_URL = "https://api.twitch.tv/helix/eventsub/subscriptions"
CALLBACK = env.callback_address
PORT = "5000"
LOCAL_ADDRESS = f"https://127.0.0.1:{PORT}"
SECRET = "abc1234def"

Base.metadata.create_all(bind=engine)
app = Flask(__name__)


# TODO: values aren't matching expected
# get sha256 value from headers
def get_secret(headers:list) -> str:
    message_id = headers["Twitch-Eventsub-Message-Id"]
    timestamp = headers["Twitch-Eventsub-Message-Timestamp"]
    body = flask_request.data

    # concatenate different headers to pass into sha256 per Twitch documentation
    hmac_message = message_id + timestamp + body.decode("utf-8")
    result = hmac_message.encode(encoding="UTF-8", errors="strict")

    # get output of sha256
    signature = hashlib.sha256(result)

    # twitch demands this concatenation for validation
    return "sha256=" + signature.hexdigest()


# check if header is valid
def validate_headers(headers:dict) -> bool:
    signature = get_secret(headers)
    expected = headers["Twitch-Eventsub-Message-Signature"]

    # check for matching sha256 values
    print("SIGNATURE CHECK")
    if signature == expected:
        print("signature is valid")
    else:
        print("signature is invalid")
    return signature == expected


# TODO: re-establish user access with correct scopes
def request_user_auth(env=env):
    url = "https://id.twitch.tv/oauth2/authorize"

    # create appropriate url for authorizing permissions
    params = {
        "client_id": env.client_id,
        "redirect_uri": f"{LOCAL_ADDRESS}/authorize",
        "response_type": "code",
        "scope": " ".join(env.scopes),
        "force_verify": "true"
    }
    get_url = url + "?" + urllib.parse.urlencode(params)

    # open browser window for user to accept required permissions
    webbrowser.open(get_url)


# write subscription parameters to the db
def store_sub_info(sub_name:str, sub_id:str, sub_type:str) -> None:
    entry = {
        "sub_name": sub_name,
        "sub_id": sub_id,
        "sub_type": sub_type
    }
    engine.execute(
        insert(Subscriptions)
        .values(entry)
    )


# create a new eventsub subscription
def create_subscription(callback:str, type_:str, env=env, content_type="application/json", 
                        url=SUB_URL, secret=SECRET) -> dict:
    headers = {
        "Client-ID": env.client_id,
        "Authorization": f"Bearer {env.get_app_access()}",
        "Content-Type": content_type
    }
    data = {
        "type": type_,
        "version": "1",
        "condition": {"broadcaster_user_id": str(env.user_id)},
        "transport": {
            "method": "webhook",
            "callback": callback,
            "secret": secret
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("SUBSCRIPTION REQUEST RESULT")
    print(response.json())
    return response.json()


# delete an active subscription by id
def delete_subscription(sub_id:str, env=env, url=SUB_URL) -> None:
    headers = {
        "Client-ID": env.client_id,
        "Authorization": f"Bearer {env.get_app_access()}"
    }
    params = {"id": sub_id}
    requests.delete(url=url, headers=headers, params=params) 


# list active subscriptions
def get_subscriptions(env=env, url=SUB_URL) -> dict:
    headers = {
        "Client-ID": env.client_id,
        "Authorization": f"Bearer {env.get_app_access()}"
    }
    response = requests.get(url=url, headers=headers)
    data = response.json()
    subs = data["data"]

    # key-values pair of sub types -> sub id
    result = {}
    for s in subs:
        result[s["type"]] = s["id"]
    return result


def refresh_user_access(env=env) -> None:
    base_url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": env.client_id,
        "client_secret": env.client_secret,
        "grant_type": "refresh_token",
        "refresh_token": env.get_refresh_token()
    }
    if scopes:
        params["scopes"] = " ".join(env.scopes)
    url = base_url + "?" + urllib.parse.urlencode(params)
    result = requests.post(url)


# default route
@app.route("/")
def hello_chat():
    request_user_auth()
    desired_subs = {
        "channel.follow": CALLBACK+"/event/new_follower",
        "channel.update": CALLBACK+"/event/stream_info_update",
        "stream.online": CALLBACK+"/event/stream_online",
        "stream.offline": CALLBACK+"/event/stream_offline",
        "channel.channel_points_custom_reward_redemption.add": CALLBACK+"/event/cp_redemption"
    }
    subs = get_subscriptions()

    # create subs that are missing
    for sub in desired_subs:
        if sub not in subs:
            create_subscription(desired_subs[sub], sub)

    subs = get_subscriptions()
    print("LIST OF CURRENT SUBSCRIPTIONS")
    print(subs)
    return Response(status=200)


# desperate attempt at authorizing
@app.route("/authorize", methods=["GET", "POST"])
def authorize():
    # get code from Twitch's POST request
    code = flask_request.args["code"]
    
    # get user access token using the above code
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": env.client_id,
        "client_secret": env.client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": f"{LOCAL_ADDRESS}/authorize"
    }
    response = requests.post(url=url, params=params)

    data = response.json()

    user_access = data["access_token"]
    refresh_token = data["refresh_token"]

    # write user access token to DB
    env.set_user_access(user_access)
    print("USER ACCESS TOKEN WRITTEN")

    # write refresh token
    env.set_refresh_token(refresh_token)     
    print("REFRESH TOKEN WRITTEN")

    return Response(status=200)


# in the event of channel point redemption
@app.route("/event/cp_redemption", methods=["POST"])
def handle_cp():
    print("CHANNEL POINTS REDEEMED!!!!")
    headers = flask_request.headers
    message_type = headers["Twitch-Eventsub-Message-Type"]

    # if callback is being used for validating a new subscription
    if message_type == "webhook_callback_verification":
        # validate webhook signature
        pass

    elif message_type == "notification":
        # handle new channel point redemption
        print("CHANNEL POINTS WERE REDEEMED!!")

    else: 
        print(flask_request.json)

    return Response(status=200)


# new follower function
@app.route("/event/new_follower", methods=["POST"])
def handle_follower():
    print("NEW FOLLOWER LINK USED!!!!!")
    headers = flask_request.headers
    message_type = headers["Twitch-Eventsub-Message-Type"]

    # if callback is being used for validating a new subscription
    if message_type == "webhook_callback_verification":
        # verify signature from POST header
        pass

    # if message is a follower notification 
    elif message_type == "notification":
        # bot sends thank you message
        # add new follower to followers table
        # change room light color
        pass

    else:
        print(flask_request.json)

    return Response(status=200)


# stream info changes
@app.route("/event/stream_info_update", methods=["POST"])
def handle_stream_info_update():
    print("STREAM UPDATE LINK USED!")
    headers = flask_request.headers
    message_type = headers["Twitch-Eventsub-Message-Type"]

    if message_type == "webhook_callback_verification":
        # validate sha256
        pass

    elif message_type == "notification":
        # handle steam info update
        pass

    else:
        print(flask_request.json)

    return Response(status=200)


# run app
if __name__ == "__main__":
    app.run(ssl_context="adhoc", port=443)


# stream goes online
@app.route("/event/stream_online", methods=["POST"])
def handle_stream_online():
    headers = flask_request.headers
    message_type = headers["Twitch-Eventsub-Message-Type"]

    if message_type == "webhook_callback_verification":
        # validate sha256
        pass

    elif message_type == "notification":
        # handle steam info update
        # run viewership tracker (once per minute)
        pass

    else:
        print(flask_request.json)

    return Response(status=200)


# stream goes offline
@app.route("/event/stream_offline", methods=["POST"])
def handle_stream_offline():
    headers = flask_request.headers
    message_type = headers["Twitch-Eventsub-Message-Type"]

    if message_type == "webhook_callback_verification":
        # validate sha256
        pass

    elif message_type == "notification":
        # handle stream offline
        # stop running view tracker
        pass

    else:
        print(flask_request.json)

    return Response(status=200)

