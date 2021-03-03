import re
import socket
import sqlite3
import command
from datetime import datetime

class Bot():
    def __init__(self, server: str, port: int, token: str, username: str, channel: str, text_commands: dict):
        self.server = server
        self.port = port
        self.oauth_token = token
        self.username = username
        self.channel = channel
        self.commands = {s.command_name: s for s in (c(self) for c in command.CommandBase.__subclasses__())}
        self.text_commands = text_commands


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
            pat_message = re.compile(fr":(?P<user>.+)!.+#{self.channel} :(?P<text>.+)", flags=re.IGNORECASE)
            
            # pull user and text from each message
            user = re.search(pat_message, message).group("user")
            text = re.search(pat_message, message).group("text")

            # respond to server pings
            if text.lower().startswith("ping"):
                print("ping received")
                self.irc_command("PONG")
                print("pong sent")

            # check for commands being used
            if text.startswith("!"):
                command = text.split()[0]
                self.execute_command(user, command, text)
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
            cursor.execute("INSERT INTO chat_messages (time, user) VALUES (:time, :user)", entry)
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
            cursor.execute("INSERT INTO command_use (time, user, command) VALUES (:time, :user, :command)", entry)
        cursor.close()
        conn.close()


    # execute each command
    def execute_command(self, user: str, command: str, message: str):
        if command in self.commands.keys():
            self.commands[command].execute(user, message)   
            self.store_command_data(user, command)

        elif command in self.text_commands.keys():
            self.send_message(
                self.channel,
                self.text_commands[command]
            )
            self.store_command_data(user, command)
        
        self.text_commands = self.reload_text_commands()


    def reload_text_commands(self):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        with conn:
            commands = {k:v for k,v in [e for e in cursor.execute("SELECT * FROM text_commands")]}
        cursor.close()
        conn.close()
        return commands
