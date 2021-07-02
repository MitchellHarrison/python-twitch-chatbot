from sqlalchemy import Integer, Text, DateTime, Column
from datetime import datetime
from database import Base

class ChatMessages(Base):
    __tablename__ = "chat_messages"

    id_ = Column("id", Integer, primary_key=True)
    time = Column("time", DateTime, default=datetime.now())
    username = Column("username", Text)
    user_id = Column("user_id", Text)
    message = Column("message", Text)

    def __init__(self):
        self.time = time
        self.username = username
        self.user_id = user_id
        self.message = message


# TODO: separate table for user info based on ID
# | user_id | anders14_ | follower or not | sub month | 
class Viewers(Base):
    __tablename__ = "viewers"

    id_ = Column("id", Integer, primary_key=True)
    username = Column("username", Text)
    display_name = Column("display_name", Text)
    is_follower = Column("is_follower", Integer)

    def __init__(self):
        pass
    

class CommandUse(Base):
    __tablename__ = "command_use"

    id_ = Column("id", Integer, primary_key=True)
    time = Column("time", DateTime, default=datetime.now())
    user = Column("user", Text)
    command = Column("command", Text)
    is_custom = Column("is_custom", Integer)

    def __init__(self):
        self.time = time
        self.user = user
        self.command = command
        self.is_custom = is_custom


class TextCommands(Base):
    __tablename__ = "text_commands"

    id_ = Column("id", Integer, primary_key=True)
    command = Column("command", Text)
    message = Column("message", Text)
    
    def __init__(self):
        self.command = command
        self.message = message


class FalseCommands(Base):
    __tablename__ = "false_commands"

    id_ = Column("id", Integer, primary_key=True)
    time = Column("time", DateTime, default=datetime.now())
    user = Column("user", Text)
    command = Column("command", Text)

    def __init__(self):
        self.time = time
        self.user = user
        self.command = command


class BotTime(Base):
    __tablename__ = "bot_time"

    id_ = Column("id", Integer, primary_key=True)
    uptime = Column("uptime", DateTime, default=datetime.now())

    def __init__(self):
        self.uptime = uptime


# list of followers by user ID and follow time
class Followers(Base):
    __tablename__ = "followers"

    user_id = Column("user_id", Integer, primary_key=True)
    time = Column("time", DateTime)
    username = Column("username", Text)

    def __init__(self):
        self.user_id = user_id
        self.time = time
        self.username = username


class FeatureRequest(Base):
    __tablename__ = "feature_requests"

    id_ = Column("id", Integer, primary_key=True)
    time = Column("time", DateTime)
    user = Column("user", Text)
    message = Column("message", Text)

    def __init__(self): 
        self.time = time
        self.user = user
        self.message = message


class Tokens(Base):
    __tablename__ = "tokens"

    id_ = Column("id", Integer, primary_key=True)
    name = Column("name", Text, unique=True)
    token = Column("token", Text)
    
    def __init__(self):
        self.name = name
        self.token = token


class Subscriptions(Base):
    __tablename__ = "subscriptions"

    id_ = Column("id", Integer, primary_key=True)
    sub_name = Column("sub_name", Text, unique=True)
    sub_id = Column("sub_id", Text, unique=True)
    sub_type = Column("sub_type", Text)

    def __init__(self):
        self.sub_name = sub_name
        self.sub_id = sub_id
        self.sub_type = sub_type


# TODO: (in progress) viewers per minute
class Viewership(Base):
    __tablename__ = "viewership"

    id_ = Column("id", Integer, primary_key=True)
    stream_id = Column("stream_id", Integer)
    title = Column("title", Text)
    category_id = Column("game_id", Text)
    category = Column("game_name", Text)
    viewers = Column("viewer_count", Integer)

    def __init__(self):
        self.stream_id = stream_id
        self.title = title
        self.game_id = game_id
        self.game = game
        self.viewer_count = viewer_count

# TODO: cp usage table
#class ChannelPointRedemptions(Base):
#    __tablename__ = "channel_point_redemptions"


