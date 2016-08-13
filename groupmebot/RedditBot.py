"""
    Ian Dansereau
    GroupMeReddit
    RedditBot.py
    5/5/16

"""
import time
from collections import OrderedDict
from enum import Enum

from groupy import Group, Bot, config
from praw import Reddit

from groupmebot.command import CommandFactory, CommandException
from groupmebot.config import Config


class RedditBotState(Enum):
    READY = 0  # ready to post image
    BUSY = 1  # checking group for new messages

    def __str__(self):
        return self.name


"""
    Bot object that will get a random image from a subreddit and post it to groupme

"""


class RedditBot(object):
    def __init__(self):
        configs = Config()
        config.KEY_LOCATION = configs.api_key

        self.config = configs

        self.groupID = configs._groupID
        self.botID = configs._botID
        self.prefix = configs._prefix
        self.nsfw = configs.nsfw
        self.admin = configs.admin
        self.reddit = Reddit("Groupme")
        self.state = RedditBotState.READY

        self.bot = [bot for bot in Bot.list() if bot.bot_id == self.botID][0]
        self.group = [group for group in Group.list() if group.group_id == self.groupID][0]

        self.currentCommand = str(self.getLatestMessage().id)
        self.commandQueue = OrderedDict()

    def getLatestMessage(self):
        return self.group.messages().newest

    def connectBot(self):
        try:
            bot = [bot for bot in Bot.list() if bot.bot_id == self.botID][0]
            group = [group for group in Group.list() if group.group_id == self.groupID][0]
            if bot is not None and group is not None:
                self.bot = bot
                self.group = group
                self.currentCommand = str(group.messages().newest.id)
                print("Successfully connected bot")
            else:
                print("Error connecting bot")
        except Exception as e:
            print("Error in connectBot(): " + e.__str__())

    def getCommands(self):
        try:
            if self.group is not None:
                messages = self.group.messages(after=self.currentCommand).filter(text__contains=self.prefix + "sr")
                if messages is not None:
                    for message in messages:
                        try:
                            command = CommandFactory(message, self).createCommand()
                            self.commandQueue[command.id] = command
                        except CommandException as e:
                            self.bot.post(str(e))
            else:
                raise Exception("group is None")
            time.sleep(0.5) #TODO: find out how much time needed between requests to stop api errors
        except Exception as e:
            print("Error in getCommands(): " + e.__str__())
            time.sleep(120) #wait 120 seconds to hopefully let the groupme request limit reset
            self.connectBot()
        finally:
            self.state = RedditBotState.READY

    def runCommands(self):
        while self.commandQueue:
            command = self.commandQueue.popitem(0)[1]
            self.currentCommand = command.id
            command.run()

    def listUserId(self):
        for member in self.group.members():
            print(member.nickname + ": " + member.user_id)

    def run(self):

        print("Running Bot")
        print("NSFW Filter=" + str(self.nsfw))

        try:
            print("Admin=" + str([member for member in self.group.members() if member.user_id == self.admin][0]))
        except IndexError:
            print("Error: Place one of the following valid AdminID's in config/config.ini:")
            self.listUserId()
            print("Running with admin features disabled")

        while True:
            try:
                if self.commandQueue:
                    if self.state == RedditBotState.READY:
                        self.runCommands()
                else:
                    self.state = RedditBotState.BUSY
                    self.getCommands()

            except Exception as e:
                print("Error in Run(): " + e.__str__())
