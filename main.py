import os
import socket
import re
import csv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv("./credentials.env")
CLIENT_ID = os.getenv("CLIENT_ID")
OAUTH_TOKEN = os.getenv("OAUTH_TOKEN")
BOT_NAME = "mitchsrobot"
CHANNEL = "mitchsworkshop"
SERVER = "irc.twitch.tv"
PORT = 6667

data_file_names = ["command_data.csv"]
data_file_paths = ["./data/"+f for f in data_file_names]

commands = [
    "!discord", 
    "!love", 
    "!github", 
    "!theme", 
    "!specs"
]

class Bot():
    def __init__(self, server, port, token, username, channel):
        self.server = server
        self.port = port
        self.oauth_token = token
        self.username = username
        self.channel = channel


    def connect_to_channel(self):
        self.irc = socket.socket()
        self.irc.connect((self.server, self.port))
        self.irc_command(f"PASS oauth:{self.oauth_token}")
        self.irc_command(f"NICK {self.username}")
        self.irc_command(f"JOIN #{self.channel}")        
        self.send_message(self.channel, "I AM ALIVE!!")
        self.check_for_messages()

    
    # execute IRC commands
    def irc_command(self, command):
        self.irc.send((command + "\r\n").encode())


    # send privmsg's, which are normal chat messages
    def send_message(self, channel, message):
        self.irc_command(f"PRIVMSG #{channel} :{message}")


    # decode incoming messages
    def check_for_messages(self):
        while True:
            messages = self.irc.recv(1024).decode()
            for m in messages.split("\r\n"):
                self.parse_message(m)


    # check for command being executed
    def parse_message(self, message):
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
        except:
            pass


    def write_command_data(self, user, command):
        entry = {
            "time": str(datetime.now()),
            "user": user,
            "command": command
        }
        field_names = entry.keys()
        with open("./data/command_data.csv", "a") as file:
            writer = csv.DictWriter(file, fieldnames = field_names)
            writer.writerow(entry)


    # define and execute each command
    def execute_command(self, user, command):
        if command in commands:
            if command == "!love":
                self.send_message(
                    self.channel, 
                    f"I love you, @{user}"
                )

            if command == "!github":
                self.send_message(
                    self.channel, 
                    "See past on-stream projects on Mitch's GitHub here! https://github.com/MitchellHarrison"
                )

            if command == "!discord":
                self.send_message(
                    self.channel, 
                    "Give or receive help or engage in nerdy debauchery in The Workshop discord server! https://discord.gg/9yFFNpP"
                )

            if command == "!theme":
                self.send_message(
                    self.channel,
                    "Current VSCode theme is Monokai Vibrant!"
                )

            if command == "!specs":
                self.send_message(
                    self.channel,
                    "CPU - i7 9700k; GPU - RTX 2080; RAM - 16GB Trident Z DDR4"
                )

            self.write_command_data(user, command)
        else:
            self.send_message(
                self.channel,
                f"That's not a valid command, @{user}"
            )


def check_for_data_files(files: list, fieldnames: list):
    for f in files:
        if f not in os.listdir("./data"):
            with open(f, "w") as file:
                writer = csv.DictWriter(file, fieldnames = fieldnames)
                writer.writeheader()


def main():
    check_for_data_files(data_file_names, ["time", "user", "command"])
    bot = Bot(SERVER, PORT, OAUTH_TOKEN, BOT_NAME, CHANNEL)
    bot.connect_to_channel()


if __name__ == "__main__":
    main()
