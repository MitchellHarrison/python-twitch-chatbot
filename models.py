from sqlalchemy import Table, Integer, Text, DateTime, Column
from datetime import datetime
from database import Base

class ChatMessages(Base):
    __tablename__ = "chat_messages"

    id = Column("id", Integer, primary_key=True)
    time = Column("time", DateTime, default=datetime.now())
    user = Column("user", Text)
    message = Column("message", Text)

    def __init__(self):
        self.time = time
        self.user = user
        self.message = message
    

class CommandUse(Base):
    __tablename__ = "command_use"

    id = Column("id", Integer, primary_key=True)
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

    id = Column("id", Integer, primary_key=True)
    command = Column("command", Text)
    message = Column("message", Text)
    
    def __init__(self):
        self.command = command
        self.message = message


class FalseCommands(Base):
    __tablename__ = "false_commands"

    id = Column("id", Integer, primary_key=True)
    time = Column("time", DateTime, default=datetime.now())
    user = Column("user", Text)
    command = Column("command", Text)

    def __init__(self):
        self.time = time
        self.user = user
        self.command = command


class BotTime(Base):
    __tablename__ = "bot_time"

    id = Column("id", Integer, primary_key=True)
    uptime = Column("uptime", DateTime, default=datetime.now())

    def __init__(self):
        self.uptime = uptime


class Followers(Base):
    __tablename__ = "followers"

    id = Column("id", Integer, primary_key=True)
    time = Column("time", DateTime)
    user_id = Column("user_id", Integer)
    username = Column("username", Text)


