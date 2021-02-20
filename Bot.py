import socket
import re
import csv
import os
import requests
import json
import random
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


    # write message author to csv
    def write_message_data(self, user):
        entry = {
            "time": str(datetime.now()),
            "user": user,
        }
        if os.path.isfile("./data/chat_count.csv"):
            with open("./data/chat_count.csv", "a") as file:
                writer = csv.writer(file)
                writer.writerow([v for k,v in entry.items()])
            
        else:
            with open("./data/chat_count.csv", "a") as file:
                writer = csv.writer(file)
                writer.writerow(entry.keys())
                writer.writerow([v for k,v in entry.items()])


    # check for command being executed
    def parse_message(self, message):
        try:
            # regex pattern
            pat_message = re.compile(r":(?P<user>.+)!.+#mitchsworkshop :(?P<text>.+)", flags=re.IGNORECASE)
            # pull user and text from each message
            user = re.search(pat_message, message).group("user")
            text = re.search(pat_message, message).group("text")

            self.write_message_data(user)

            # check for commands being used
            if text.startswith("!"):
                command = text.split()[0]
                self.execute_command(user, command)
        except:
            pass

    
    # write command usage data to CSV
    def write_command_data(self, user, command):
        entry = {
            "time": str(datetime.now()),
            "user": user,
            "command": command
        }
        if os.path.isfile("./data/command_data.csv"):
            with open("./data/command_data.csv", "a") as file:
                writer = csv.writer(file)
                writer.writerow([v for k,v in entry.items()])
            
        else:
            with open("./data/command_data.csv", "a") as file:
                writer = csv.writer(file)
                writer.writerow(entry.keys())
                writer.writerow([v for k,v in entry.items()])


    # execute each command
    def execute_command(self, user, command):
        if command in self.commands.keys():
            self.commands[command].execute(user)   
            self.write_command_data(user, command)
