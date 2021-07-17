import requests
import re
import random
import json
from datetime import datetime
from dateutil import relativedelta
from abc import ABC, abstractmethod
from sqlalchemy import select, insert, delete, update, func
from database import engine, Session, Base
from models import BotTime, Followers, TextCommands, ChatMessages, CommandUse, FeatureRequest
from environment import env

Base.metadata.create_all(bind=engine)
session = Session()

class CommandBase(ABC):
    def __init__(self, bot):
        self.bot = bot


    @property
    @abstractmethod
    def command_name(self):
        raise NotImplementedError


    @property
    def restricted(self):
        return False


    @abstractmethod
    def execute(self):
        raise NotImplementedError


    def __repr__(self):
        return self.command_name


    def get_commands(self):
        # get all text commands
        result = engine.execute(select(TextCommands.command)).fetchall()
        text_commands = [c[0] for c in result]
        return [*text_commands, *self.bot.commands] 


    def get_command_users(self, command):
        # query database for number of times each user used a given command
        result = engine.execute(
            select(CommandUse.user)
            .where(CommandUse.command == command)
            .group_by(CommandUse.user)
            .order_by(func.count(CommandUse.user).desc())
        )
        return [u[0] for u in result]


    def get_top_chatters(self):
        # get count of unique chatters from chat_messages table
        result = engine.execute(
            select(ChatMessages.username)
            .group_by(ChatMessages.username)
            .order_by(func.count(ChatMessages.username).desc())
        )
        return [u[0] for u in result]


class AddCommand(CommandBase):
    @property
    def command_name(self):
        return "!addcommand"

    @property
    def restricted(self):
        return True

    def execute(self, user, message, badges):
        # only mods can run this command
        if "moderator" in badges or "broadcaster" in badges:
            first_word = message.split()[1].lower()

            # check for invalid characters in command name
            if re.match(r"[^a-zA-Z\d]", first_word):
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = f"That command name contains invalid characters, {user}."
                )
                return

            command = first_word if first_word.startswith("!") else "!" + first_word
            result = " ".join(message.split()[2:])

            # check for missing command output
            if len(result) == 0:
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = f"Every command needs text, {user}."
                )
                return

            # check for duplicate command
            if command in self.bot.text_commands.keys():
                self.bot.send_message(
                    self.bot.channel,
                    f"That command already exists, {user}."
                )
                return

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

    @property
    def restricted(self):
        return True

    def execute(self, user, message, badges):
        # only mods can run this command
        if "moderator" in badges or "broadcaster" in badges:
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
                f"{command} command deleted!"
            )


# edit existing text command
class EditCommand(CommandBase):
    @property
    def command_name(self):
        return "!editcommand"

    @property
    def restricted(self):
        return True

    def execute(self, user, message, badges):
        # only mods and streamer can run this command
        if "moderator" in badges or "broadcaster" in badges:
            first_word = message.split()[1]
            command = first_word if first_word.startswith("!") else "!" + first_word

            result = engine.execute(select(TextCommands.command)).fetchall()
            current_commands = [c[0] for c in result]

            if command not in current_commands:
                self.bot.send_message(
                    self.bot.channel,
                    f"That command doesn't exist, {user}."
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
                f"{command} command edit complete!"
            )


# check joke API for joke of length that fits in a chat message
class JokeCommand(CommandBase):
    @property
    def command_name(self):
        return "!joke"


    def execute(self, user, message, badges):
        max_message_len = 500
        url = "https://icanhazdadjoke.com/"
        headers = {"accept" : "application/json"}
        for _ in range(10):
            result = requests.get(url, headers = headers).json()
            joke = result["joke"]
            if len(joke) <= max_message_len:
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = joke
                )
                return
        self.bot.send_message(
            channel = self.bot.channel,
            message = f"I'm sorry! I couldn't find a short enough joke. :("
        )


class PoemCommand(CommandBase):
    @property
    def command_name(self):
        return "!poem"


    def execute(self, user, message, badges):
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
                return
        self.bot.send_message(
            channel = self.bot.channel,
            message = f"@{user}, I couldn't find a short enough poem. I'm sorry. :("
        )


class CommandsCommand(CommandBase):
    @property
    def command_name(self):
        return "!commands"


    def execute(self, user, message, badges):
        result = engine.execute(select(TextCommands.command)).fetchall()
        subclasses = (s(self) for s in CommandBase.__subclasses__())
        text_commands = [c[0] for c in result]
        hard_commands = [c.command_name for c in subclasses if not c.restricted]

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


# TODO: fill follower table with new script, update with eventsub
#class FollowAgeCommand(CommandBase):
#    @property
#    def command_name(self):
#        return "!followage"
#
#
#    def execute(self, user, message, badges):
#        if len(message.split()) > 1:
#            user = message.split()[1].strip("@").lower()
#
#        # get user's follow time
#        user_entry = engine.execute(
#            select(Followers.time)
#            .where(Followers.username == user)
#        ).fetchone()
#
#        follow_time = user_entry[0]
#        
#        # current time
#        now = datetime.now()
#
#        # get time delta
#        delta = relativedelta.relativedelta(now, follow_time)
#        follow_stats = {
#            "year": delta.years,
#            "month": delta.months,
#            "day": delta.days,
#            "hour": delta.hours,
#            "minute": delta.minutes
#        }
#
#        # create message
#        message = f"{user} has been following for"
#        for k,v in follow_stats.items():
#            if v > 0:
#                message += f" {v} {k}"
#                if v > 1:
#                    message += "s"
#        message += "!"
#
#        # send message
#        self.bot.send_message(
#            channel = self.bot.channel,
#            message = message
#        )


class BotTimeCommand(CommandBase):
    @property
    def command_name(self):
        return "!bottime"


    def execute(self, user, message, badges):
        # get most recent uptime
        result = engine.execute(
            select(BotTime.uptime)
            .order_by(BotTime.id_.desc())
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


    def execute(self, user, message, badges):
        if len(message.split()) > 1:
            command = message.split()[1]
            # command use rank
            if not command.startswith("!"):
                command = f"!{command}"

            commands = self.get_commands()

            if command not in commands:
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = f"I don't have a {command} command! Sorry!"
                )
                return

            # query database for number of times each user used a given command
            users = self.get_command_users(command)

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
            chatters = self.get_top_chatters()

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


    def execute(self, user, message, badges):
        entry = {
                "user": user, 
                "message": " ".join(message.split()[1:])
            }
        engine.execute(
            insert(FeatureRequest)
            .values(entry)
        )

        self.bot.send_message(
            channel = self.bot.channel,
            message = f"Got it! Thanks for your help, {user}!"
        )


class LurkCommand(CommandBase):
    @property
    def command_name(self):
        return "!lurk"

    
    def execute(self, user, message, badges):
        self.bot.send_message(
            channel = self.bot.channel,
            message = f"Don't worry {user}, we got mad love for the lurkers! <3"
        )
        

class ShoutoutCommand(CommandBase):
    @property
    def command_name(self):
        return "!so"


    def execute(self, user, message, badges):
        # check if user shouting out no one
        if len(message.split()) < 2:
            self.bot.send_message(
                channel = self.bot.channel,
                message = f"I can't shoutout no one, {user}!"
            )

        # if shouting someone
        else:
            so_user = message.split()[1].strip("@")

            # correct for users trying to shout themselves out
            if user.lower() == so_user.lower():
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = f"You can't shoutout yourself, {user}!"
                )
                return

            # api only returns users that have streamed in the past six months
            url = f"https://api.twitch.tv/helix/search/channels?query={so_user}"
            headers = {
                "client-id" : env.client_id,
                "authorization" : f"Bearer {env.get_bearer()}"
            }

            response = requests.get(url, headers=headers)
            data = json.loads(response.content)["data"][0]
            so_display_name = data["display_name"]
            so_login = data["broadcaster_login"]

            # validates that user is real
            # TODO: can't find absenth762 specifically
            if so_user.lower() == so_login:
                so_url = f"https://twitch.tv/{so_login}"
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = f"Shoutout to {so_display_name}! Check them out here! {so_url}"
                )

            # user could not exist or not have streamed in 6 months
            else:
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = f"{so_user} isn't a frequent streamer, {user}."
                )


# TODO: !leaderboard command
class LeaderboardCommand(CommandBase):
    @property
    def command_name(self):
        return "!leaderboard"


    def execute(self, user, message, badges):
        if len(message.split()) > 1:
            # command-specific leaderboard
            command = message.split()[1]
            if not command.startswith("!"):
                command = "!"+command
            
            commands = self.get_commands()
            if command not in commands:
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = f"Sorry {user}, that command doesn't exist!"
                )
                return

            users = self.get_command_users(command)

        else:
            users = self.get_top_chatters()
            
        top_n = 5
        leaders = users[:top_n]
        message_ranks = [f"{i}. {user}" for i,user in enumerate(leaders, start=1)]
        print(message_ranks)

        self.bot.send_message(
            channel = self.bot.channel,
            message = ", ".join(message_ranks)
        )


class AliasCommand(CommandBase):
    @property
    def command_name(self):
        return "!clone"

    @property
    def restricted(self):
        return True


    # this function adds an alias to the text_commands table
    def add_alias(self, command, alias):
        entry = {
            "command": alias,
            "message": self.bot.text_commands[command]
        }
        engine.execute(
            insert(TextCommands)
            .values(entry)
        )
    

    def execute(self, user, message, badges):
        if "moderator" in badges or "broadcaster" in badges:
            params = message.split()
            # correct if user doesn't pass enough parameters
            if len(params) < 3:
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = f"You didn't give me enough direction, {user}. I am now lost in this world. :("
                )
                return

            else:
                # set commands to be aliases of one another
                command1 = params[1] if params[1].startswith("!") else f"!{params[1]}"
                command2 = params[2] if params[2].startswith("!") else f"!{params[2]}"


                if command1 in self.bot.text_commands:
                    self.add_alias(command1, command2)

                elif command2 in self.bot.text_commands:
                    self.add_alias(command2, command1)
                    
                # if neither command is a text command
                else:
                    self.bot.send_message(
                        channel = self.bot.channel,
                        message = f"I don't have those commands, {user}. Sorry!"
                    )
                    return

                self.bot.send_message(
                    channel = self.bot.channel, 
                    message = "Clone created!"
                )


# fun fact command
class FactCommand(CommandBase):
    @property
    def command_name(self):
        return "!fact"


    def execute(self, user, message, badges):
        url = "https://uselessfacts.jsph.pl/random.json?language=en"
        response = requests.get(url).json()
        fact = response["text"]

        # check that fact fits in a chat message
        while len(fact) > 450:
            response =requests.get(url).json()
            fact = response["text"]

        self.bot.send_message(
            channel = self.bot.channel,
            message = f"FUN FACT: {fact}"
        )
