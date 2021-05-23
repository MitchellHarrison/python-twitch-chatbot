import requests
import random
import json
from datetime import datetime
from dateutil import relativedelta
from abc import ABC, abstractmethod
from sqlalchemy import select, insert, delete, update, func
from database import engine, Session, Base
from models import BotTime, Followers, TextCommands, ChatMessages, CommandUse, FeatureRequests

Base.metadata.create_all(bind=engine)
session = Session()

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
                    f"That command already exists, {user}."
                )
                return

            # TODO:
            entry = {"command":command, "message":result}
            engine.execute(
                insert(TextCommands)
                .values(entry)
            )

            self.bot.send_message(
                self.bot.channel,
                f"{command} added successfully!"
            )


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

            # select all commands from TextCommands table
            result = engine.execute(select(TextCommands.command)).fetchall()
            current_commands = [c[0] for c in result]

            if command not in current_commands:
                self.bot.send_message(
                    self.bot.channel,
                    f"The {command} command doesn't exist, {user}."
                )
                return

            entry = {"command": command}

            engine.execute(
                delete(TextCommands)
                .where(TextCommands.command == command)
            )

            self.bot.send_message(
                self.bot.channel,
                f"{command} command deleted, @{user}."
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

            result = engine.execute(select(TextCommands.command)).fetchall()
            current_commands = [c[0] for c in result]

            if command not in current_commands:
                self.bot.send_message(
                    self.bot.channel,
                    f"That command doesn't exist, @{user}."
                )
                return

            new_message = " ".join(message.split()[2:])

            # edit the message for a given command
            engine.execute(
                update(TextCommands)
                .where(TextCommands.command == command)
                .values(message=new_message)
            )
            
            self.bot.send_message(
                self.bot.channel,
                f"{command} command edit complete {user}!"
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
        result = engine.execute(select(TextCommands.command)).fetchall()
        text_commands = [c[0] for c in result]
        hard_commands = [c.command_name for c in (s(self) for s in CommandBase.__subclasses__())]
        commands_str = ", ".join(text_commands) + ", " + ", ".join(hard_commands)

        # TODO: hide admin commands
        for comm in ["!addcommand", "!delcommand", "!editcommand"]:
            commands_str.replace(comm+",", "")

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
        if len(message.split()) > 1:
            user = message.split()[1].strip("@").lower()

        user_entry = engine.execute(
            select(Followers.time)
            .where(Followers.username == user)
        ).fetchone()
        follow_time = user_entry[0]
        now = datetime.now()

        delta = relativedelta.relativedelta(now, follow_time)
        follow_stats = {
            "year": delta.years,
            "month": delta.months,
            "day": delta.days,
            "hour": delta.hours,
            "minute": delta.minutes
        }

        message = f"{user} has been following for"
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


class BotTimeCommand(CommandBase):
    @property
    def command_name(self):
        return "!bottime"


    def execute(self, user, message):
        # get most recent uptime
        result = engine.execute(
            select(BotTime.uptime)
            .order_by(BotTime.id.desc())
        ).fetchone()
        uptime = result[0]

        now = datetime.now()

        # get timedelta
        delta = relativedelta.relativedelta(now, uptime)
        uptime_stats = {
            "year": delta.years,
            "month": delta.months,
            "day": delta.days,
            "hour": delta.hours,
            "minute": delta.minutes
        }

        # send specific message if bot has been alive for under a minute
        if all(v==0 for v in uptime_stats.values()):
            self.bot.send_message(
                channel = self.bot.channel,
                message = f"Give me a minute, {user}! I just woke up!"
            )
            return

        # build output message
        message = f"I have been alive for"
        for k,v in uptime_stats.items():
            if v > 0:
                message += f" {v} {k}"
                if v > 1:
                    message += "s"
        message += "!"

        self.bot.send_message(
            channel = self.bot.channel,
            message = message
        )


class RankCommand(CommandBase):
    @property
    def command_name(self):
        return "!rank"


    def execute(self, user, message):
        if len(message.split()) > 1:
            command = message.split()[1]
            # command use rank
            if not command.startswith("!"):
                command = f"!{command}"

            # get all text commands
            result = engine.execute(select(TextCommands.command)).fetchall()
            text_commands = [c[0] for c in result]

            commands = [*text_commands, *self.bot.commands] 

            if command not in commands:
                self.bot.send_message(
                        channel = self.bot.channel,
                        message = f"That is not a command that I have. Sorry!"
                    )
                return

            # query database for number of times each user used a given command
            result = engine.execute(
                select(CommandUse.user)
                .where(CommandUse.command == command)
                .group_by(CommandUse.user)
                .order_by(func.count(CommandUse.user).desc())
            )
            users = [u[0] for u in result]

            try:
                user_rank = users.index(user) + 1
            except ValueError:
                self.bot.send_message(
                        channel = self.bot.channel,
                        message = f"{user}, you haven't used that command since I've been listening. Sorry!"
                    )
                return
            message = f"{user}, you are the number {user_rank} user of the {command} command out of {len(users)} users."
            self.bot.send_message(
                    channel = self.bot.channel,
                    message = message
                    )

        else:
            # get count of unique chatters from chat_messages table
            result = engine.execute(
                select(ChatMessages.user)
                .group_by(ChatMessages.user)
                .order_by(func.count(ChatMessages.user).desc())
            )
            chatters = [u[0] for u in result]

            try:
                # find rank of a given user
                user_rank = chatters.index(user) + 1

                # send the rank in chat
                message = f"{user}, you are number {user_rank} out of {len(chatters)} chatters!"
                self.bot.send_message(
                        channel = self.bot.channel,
                        message = message
                    )

            except ValueError:
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = f"{user}, I don't have you on my list. This is awkward..."
                )

            
class FeatureRequestCommand(CommandBase):
    @property
    def command_name(self):
        return "!featurerequest"


    def execute(self, user, message):
        entry = {
                "user": user, 
                "message": message
            }
        engine.execute(
            insert(FeatureRequests)
            .values(entry)
        )

        self.bot.send_message(
            channel = self.bot.channel,
            message = f"Got it! Thanks for your help, {user}!"
        )


# TODO: !lurk thanks people by name for lurking


# TODO: !so command links someone's Twitch channel by using their name to build their URL
# should require a second word after "so!" to prevent people shouting themselves out
# should check to make sure that the user name in question isn't the senders
# should verify that the person being shouted out actually exists
