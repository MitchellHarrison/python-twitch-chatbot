import requests
import random
import json
import sqlite3
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

class CommandBase(ABC):
    def __init__(self, bot):
        self.bot = bot


    @property 
    @abstractmethod
    def command_name(self):
        raise NotImplementedError
    
    
    @abstractmethod 
    def execute(self):
        raise NotImplementedError


    def __repr__(self):
        return self.command_name


# TODO: !addcommand
class AddCommand(CommandBase):
    @property
    def command_name(self):
        return "!addcommand"


    def execute(self, user, message):
        if user == self.bot.channel:
            first_word = message.split()[1]
            command = first_word if first_word.startswith("!") else "!" + first_word
            result = " ".join(message.split()[2:])

            if command in self.bot.text_commands.keys():
                self.bot.send_message(
                    self.bot.channel,
                    f"That command doesn't exist, @{user}."
                )
                return

            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            entry = {
                "command" : command,
                "message" : result
            }
            with conn:
                cursor.execute("INSERT INTO text_commands (command, message) VALUES (:command, :message);", entry)
            cursor.close()
            conn.close()
            self.bot.send_message(
                self.bot.channel,
                f"{command} added successfully!"
            )


# delete existing text command
class DeleteCommand(CommandBase):
    @property 
    def command_name(self):
        return "!delcommand"


    def execute(self, user, message):
        if user == self.bot.channel:
            try:
                first_word = message.split()[1]
            except IndexError:
                self.bot.send_message(
                    self.bot.channel,
                    "You didn't select a command to delete!"
                )
                return

            command = first_word if first_word.startswith("!") else "!" + first_word

            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT command FROM text_commands;")
            conn.commit()
            current_commands = [c[0] for c in cursor.fetchall()]
            if command not in current_commands:
                self.bot.send_message(
                    self.bot.channel,
                    f"The {command} command doesn't exist, @{user}."
                )
                return
            
            cursor.execute(f"DELETE FROM text_commands WHERE command = '{command}';")
            conn.commit()
            cursor.close()
            conn.close()
            self.bot.send_message(
                self.bot.channel,
                f"!{command} command deleted, @{user}."
            )


# edit existing text command
class EditCommand(CommandBase):
    @property
    def command_name(self):
        return "!editcommand"

    
    def execute(self, user, message):
        if user == self.bot.channel:
            first_word = message.split()[1]
            command = first_word if first_word.startswith("!") else "!" + first_word

            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT command FROM text_commands;")
            current_commands = [c[0] for c in cursor.fetchall()]

            if command not in current_commands:
                self.bot.send_message(
                    self.bot.channel,
                    f"That command doesn't exist, @{user}."
                )
                return 
            
            new_message = " ".join(message.split()[2:])
            cursor.execute(f"UPDATE text_commands SET message = '{new_message}' WHERE command = '{command}';")
            conn.commit()
            cursor.close()
            conn.close()
            self.bot.send_message(
                self.bot.channel,
                f"{command} command edit complete @{user}!"
            )


class JokeCommand(CommandBase):
    @property
    def command_name(self):
        return "!joke"

    
    def execute(self, user, message):
        url = "https://icanhazdadjoke.com/"
        headers = {"accept" : "application/json"}
        for _ in range(10):
            result = requests.get(url, headers = headers).json()
            joke = result["joke"]
            if len(joke) <= 500:
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = joke
                )
                break
        self.bot.send_message(
            channel = self.bot.channel,
            message = f"I'm sorry! I couldn't find a short enough joke. :("
        )


class PoemCommand(CommandBase):
    @property
    def command_name(self):
        return "!poem"
    

    def execute(self, user, message):
        num_lines = 4
        url = f"https://poetrydb.org/linecount/{num_lines}/lines"
        result = requests.get(url)
        poems = json.loads(result.text)
        num_poems = len(poems)
        for _ in range(5):
            idx = random.randint(0, num_poems)
            lines = poems[idx]["lines"]
            poem = "; ".join(lines)
            if len(poem) <= 500:
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = poem
                )
        self.bot.send_message(
            channel = self.bot.channel,
            message = f"@{user}, I couldn't find a short enough poem. I'm sorry. :("
        )


class CommandsCommand(CommandBase):
    @property 
    def command_name(self):
        return "!commands"

    
    def execute(self, user, message):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        with conn:
            cursor.execute("SELECT command FROM text_commands")
            text_commands = [t[0] for t in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        hard_commands = [c.command_name for c in (s(self) for s in CommandBase.__subclasses__())]
        commands_str = ", ".join(text_commands) + ", " + ", ".join(hard_commands)
        
        # check if commands fit in chat; dropping 
        while len(commands_str) > 500:
            commands = commands_str.split()
            commands = commands[:-2]
            commands_str = " ".join(commands)
        
        self.bot.send_message(
            channel = self.bot.channel,
            message = commands_str
        )


class FollowAgeCommand(CommandBase):
    @property 
    def command_name(self):
        return "!followage"

    
    def execute(self, user, message):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        if len(message.split()) > 1:
            user = message.split()[1]

        with conn:
            cursor.execute(f"""SELECT time FROM followers
                                WHERE username='{user.lower()}'""")
            try:
                follow_time_str = cursor.fetchone()[0]
            except TypeError:
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = f"{user} is not currently following {self.bot.channel} or is a new follower."
                )
                return
        cursor.close()
        conn.close()
        
        follow_time = datetime.strptime(follow_time_str, "%Y-%m-%dT%H:%M:%SZ")
        delta = datetime.now() - follow_time

        years = delta.days // 365
        days = delta.days - (years*365)
        hours = delta.seconds // 3600
        minutes = (delta.seconds - hours*3600) // 60
        seconds = delta.seconds - (hours * 3600) - (minutes * 60)
        follow_stats = {
            "year" : years,
            "day" : days,
            "hour" : hours,
            "minute" : minutes,
            "second" : seconds
        }

        message = f"@{user} has been following for"
        for k,v in follow_stats.items():
            if v > 0:
                message += f" {v} {k}"
                if v > 1:
                    message += "s"
        message += "!"
        self.bot.send_message(
            channel = self.bot.channel,
            message = message
        )


# class UptimeCommand(CommandBase):
#     @property
#     def command_name(self):
#         return "!uptime"

    
#     def execute(self, user, message):
#         url = f"https://api.twitch.tv/helix/streams?user_id={self.bot.user_id}"
#         headers = {
#             "client-id": self.bot.client_id,
#             "authorization" : f"Bearer {self.bot.bearer}"
#         }
#         response = requests.get(url, headers = headers, timeout=3)
#         data = json.loads(response.content)
#         start_time = data["data"][0]["started_at"]
#         # try:
#         #     start_time = data["data"][0]["started_at"]
#         # except KeyError:
#         #     self.bot.send_message(
#         #         channel = self.bot.channel,
#         #         message = f"{self.bot.channel} is not currently live! :("
#         #     )
#         #     return     

#         delta = datetime.now() - start_time

#         years = delta.days // 365
#         days = delta.days - (years*365)
#         hours = delta.seconds // 3600
#         minutes = (delta.seconds - hours*3600) // 60
#         seconds = delta.seconds - (hours * 3600) - (minutes * 60)

#         follow_stats = {
#             "year" : years,
#             "day" : days,
#             "hour" : hours,
#             "minute" : minutes,
#             "second" : seconds
#         }

#         message = f"@{user}, {self.bot.channel} has been live for"
#         for k,v in follow_stats.items():
#             if v > 0:
#                 message += f" {v} {k}"
#                 if v > 1:
#                     message += "s"
#         message += "!"

#         self.bot.send_message(
#             channel = self.bot.channel,
#             message = message
#         )
