import socket
import re
import sqlite3
import Command
from datetime import datetime

class Bot():
    def __init__(self, server, port, token, username, channel):
        self.server = server
        self.port = port
        self.oauth_token = token
        self.username = username
        self.channel = channel
        self.commands = {s.command_name: s for s in (c(self) for c in Command.CommandBase.__subclasses__())}


    # connect to IRC server and begin checking for messages
    def connect_to_channel(self):
        self.irc = socket.socket()
        self.irc.connect((self.server, self.port))
        self.irc_command(f"PASS oauth:{self.oauth_token}")
        self.irc_command(f"NICK {self.username}")
        self.irc_command(f"JOIN #{self.channel}")        
        self.send_message(self.channel, "I AM ALIVE!!")
        self.check_for_messages()

    
    # execute IRC commands
    def irc_command(self, command: str):
        self.irc.send((command + "\r\n").encode())


    # send privmsg's, which are normal chat messages
    def send_message(self, channel: str, message: str):
        self.irc_command(f"PRIVMSG #{channel} :{message}")


    # decode incoming messages
    def check_for_messages(self):
        while True:
            messages = self.irc.recv(1024).decode()
            for m in messages.split("\r\n"):
                self.parse_message(m)


    # check for command being executed
    def parse_message(self, message: str):
        try:
            # regex pattern
            pat_message = re.compile(r":(?P<user>.+)!.+#mitchsworkshop :(?P<text>.+)", flags=re.IGNORECASE)
            # pull user and text from each message
            user = re.search(pat_message, message).group("user")
            text = re.search(pat_message, message).group("text")

            # check for commands being used
            if text.startswith("!"):
                command = text.split()[0]
                self.execute_command(user, command)
            self.store_message_data(user)

        except AttributeError:
            pass

    
    # insert data to SQLite db
    def store_message_data(self, user: str):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        entry = {
            "time" : str(datetime.now()),
            "user" : user
        }
        with conn:
            cursor.execute("INSERT INTO chat_messages VALUES (:time, :user)", entry)
        cursor.close()
        conn.close()


    # insert data to SQLite db
    def store_command_data(self, user: str, command: str):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        entry = {
            "time" : str(datetime.now()),
            "user" : user,
            "command" : command
        }
        with conn:
            cursor.execute("INSERT INTO command_use VALUES (:time, :user, :command)", entry)
        cursor.close()
        conn.close()

        # execute each command
    def execute_command(self, user: str, command: str):
        if command in self.commands.keys():
            self.commands[command].execute(user)   
            self.store_command_data(user, command)
