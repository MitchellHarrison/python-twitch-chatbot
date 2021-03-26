import re
import socket
import sqlite3
import command
from datetime import datetime

class Bot():
    def __init__(self, server: str, port: int, oauth_token: str, bot_name: str, channel: str, user_id: str, client_id: str, text_commands: dict):
        self.server = server
        self.port = port
        self.oauth_token = oauth_token
        self.bot_name = bot_name
        self.channel = channel
        self.user_id = user_id
        self.client_id = client_id
        self.commands = {s.command_name: s for s in (c(self) for c in command.CommandBase.__subclasses__())}
        self.text_commands = text_commands


    # connect to IRC server and begin checking for messages
    def connect_to_channel(self):
        self.irc = socket.socket()
        self.irc.connect((self.server, self.port))
        self.irc_command(f"PASS oauth:{self.oauth_token}")
        self.irc_command(f"NICK {self.bot_name}")
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
            print(">" + messages)

            # respond to pings from Twitch
            if messages.startswith("PING"):
                self.irc_command("PONG :tmi.twitch.tv")
                
            for m in messages.split("\r\n"):
                self.parse_message(m)


    # check for command being executed
    def parse_message(self, message: str):
        try:
            # regex pattern
            pat_message = re.compile(fr":(?P<user>.+)!.+#{self.channel} :(?P<text>.+)", flags=re.IGNORECASE)
            
            # pull user and text from each message
            user = re.search(pat_message, message).group("user")
            message = re.search(pat_message, message).group("text")

            # respond to server pings
            if message.lower().startswith("ping"):
                print("ping received")
                self.irc_command("PONG")
                print("pong sent")

            # check for commands being used
            if message.startswith("!"):
                command = message.split()[0].lower()
                if command not in self.text_commands and command not in self.commands:
                    self.store_wrong_command(user, command)
                else:
                    self.execute_command(user, command, message)
            self.store_message_data(user, message)

        except AttributeError:
            pass

    
    # store data on commands attempted that don't exist
    def store_wrong_command(self, user: str, command: str):
        entry = {
            "time" : datetime.now(),
            "user" : user,
            "command" : command
        }
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        with conn:
            cursor.execute("INSERT INTO false_commands (time, user, command) VALUES (:time, :user, :command)", entry)
        cursor.close()
        conn.close()
        

    # insert data to SQLite db
    def store_message_data(self, user: str, message: str):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        entry = {
            "time" : str(datetime.now()),
            "user" : user,
            "message" : message
        }
        with conn:
            cursor.execute("INSERT INTO chat_messages (time, user, message) VALUES (:time, :user, :message)", entry)
        cursor.close()
        conn.close()


    # insert data to SQLite db
    def store_command_data(self, user: str, command: str, is_custom: int):
        entry = {
            "time" : str(datetime.now()),
            "user" : user,
            "command" : command,
            "is_custom" : is_custom
        }
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        with conn:
            cursor.execute("""INSERT INTO command_use (time, user, command, is_custom) 
                                VALUES (:time, :user, :command, :is_custom)""", entry)
        cursor.close()
        conn.close()


    # execute each command
    def execute_command(self, user: str, command: str, message: str):
        # execute hard-coded command
        if command in self.commands.keys():
            self.commands[command].execute(user, message) 
            is_custom_command = 0 
            self.store_command_data(user, command, is_custom_command)

        # execute custom text commands
        elif command in self.text_commands.keys():
            self.send_message(
                self.channel,
                self.text_commands[command]
            )
            is_custom_command = 1
            self.store_command_data(user, command, is_custom_command)
        
        self.text_commands = self.reload_text_commands()


    def reload_text_commands(self):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        with conn:
            commands = {k:v for k,v in [e for e in cursor.execute("SELECT * FROM text_commands")]}
        cursor.close()
        conn.close()
        return commands
