import requests
import random
import json
from abc import ABC, abstractmethod

class CommandBase(ABC):
    def __init__(self, bot):
        self.bot = bot


    @abstractmethod 
    def execute(self):
        raise NotImplementedError


    @property 
    @abstractmethod
    def command_name(self):
        raise NotImplementedError


    def __repr__(self):
        return f"Command: {self.command_name}"


class DiscordCommand(CommandBase):
    @property 
    def command_name(self):
        return "!discord"


    def execute(self, user):
        self.bot.send_message(
            channel = self.bot.channel, 
            message = f"@{user}, Give or receive help or engage in nerdy debauchery in The Workshop discord server! https://discord.gg/9yFFNpP"
        )


class GithubCommand(CommandBase):
    @property 
    def command_name(self):
        return "!github"

    
    def execute(self, user):
        self.bot.send_message(
            channel = self.bot.channel,
            message = f"@{user}, See past on-stream projects on Mitch's GitHub here! https://github.com/MitchellHarrison"
        )
    

class TwitterCommand(CommandBase):
    @property 
    def command_name(self):
        return "!twitter"


    def execute(self, user):
        self.bot.send_message(
            channel = self.bot.channel,
            message = f"@{user}, Twitter is your one-stop-shop for streams of consciousness and Macswell pics!  https://twitter.com/MitchsWorkshop"
        )  


class ThemeCommaned(CommandBase):
    @property
    def command_name(self):
        return "!theme"


    def execute(self, user):
        self.bot.send_message(
                channel = self.bot.channel,
                message = f"@{user}, Current VSCode theme is Monokai Vibrant!"
            )      


class JokeCommand(CommandBase):
    @property
    def command_name(self):
        return "!joke"

    
    def execute(self, user):
        url = "https://geek-jokes.sameerkumar.website/api?format=json"
        for _ in range(10):
            result = requests.get(url).json()
            joke = result["joke"]
            if len(joke) <= 500:
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = joke
                )
        self.bot.send_message(
            channel = self.bot.channel,
            message = f"I'm sorry @{user}! I couldn't find a short enough joke. :("
        )


class PoemCommand(CommandBase):
    @property
    def command_name(self):
        return "!joke"
    

    def execute(self, user):
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

