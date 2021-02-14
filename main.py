import os
import socket
import re
from dotenv import load_dotenv

load_dotenv("./credentials.env")
CLIENT_ID = os.getenv("CLIENT_ID")
OAUTH_TOKEN = os.getenv("OAUTH_TOKEN")
BOT_NAME = "mitchsrobot"
CHANNEL = "mitchsworkshop"

class Bot():
    def __init__(self):
        self.server = "irc.twitch.tv"
        self.port = 6667
        self.oauth_token = OAUTH_TOKEN
        self.username = BOT_NAME
        self.channel = CHANNEL


    def connect_to_channel(self):
        self.irc = socket.socket()
        self.irc.connect((self.server, self.port))
        self.irc_command(f"PASS oauth:{self.oauth_token}")
        self.irc_command(f"NICK {self.username}")
        self.irc_command(f"JOIN #{self.channel}")        
        self.send_message(self.channel, "Happy Valentine's Day, everyone! <3")
        self.check_for_messages()


    def irc_command(self, command):
        self.irc.send((command + "\r\n").encode())


    def send_message(self, channel, message):
        self.irc_command(f"PRIVMSG #{channel} :{message}")


    def check_for_messages(self):
        while True:
            messages = self.irc.recv(1024).decode()
            for m in messages.split("\r\n"):
                self.parse_message(m)


    def parse_message(self, message):
        try:
            pat_message = re.compile(r":(?P<user>.+)!.+#mitchsworkshop :(?P<text>.+)", flags=re.IGNORECASE)
            user = re.search(pat_message, message).group("user")
            text = re.search(pat_message, message).group("text")
            print(f"{user} - {text}")
            if text.startswith("!"):
                command = text.split()[0]
                self.execute_command(user, command) 
        except:
            pass


    def execute_command(self, user, command):
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


bot = Bot()
bot.connect_to_channel()
