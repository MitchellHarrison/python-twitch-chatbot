import requests
import random
import json
import sqlite3
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
        return f"Command: {self.command_name}"


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
                cursor.execute("INSERT INTO text_commands (command, message) VALUES (:command, :message)", entry)
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
            first_word = message.split()[1]
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
            cursor.execute("SELECT command FROM text_commands")
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
        url = "https://geek-jokes.sameerkumar.website/api?format=json"
        for _ in range(10):
            result = requests.get(url).json()
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
