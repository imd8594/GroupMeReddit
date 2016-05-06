"""
    Ian Dansereau
    GroupMeReddit
    RedditBot.py
    5/5/16

"""
import mimetypes
import random
from urllib.parse import urlparse

from groupy import Group, Bot, config
from praw import Reddit, errors
from enum import Enum

from groupmebot.config import Config


class RedditBotState(Enum):
    READY = 0  # polling groupme for new messages containing command
    BUSY = 1  # searching for image, and posting image

    def __str__(self):
        return self.name


"""
    Bot object that will get a random image from a subreddit and post it to groupme

"""
class RedditBot(object):
    def __init__(self):
        configs = Config()
        config.KEY_LOCATION = configs.api_key

        self.admin = configs.admin
        self.groupID = configs._groupID
        self.botID = configs._botID
        self.prefix = configs._prefix
        self.nsfw = configs.nsfw

        self.bot = [bot for bot in Bot.list() if bot.bot_id == self.botID][0]
        self.group = [group for group in Group.list() if group.group_id == self.groupID][0]

        self.state = RedditBotState.READY
        self.currentCommand = str(self.getLatestMessage().id)
        self.commandQueue = []


    def postImage(self, subreddit=None):
        link = self.getRandomImage(subreddit)
        self.bot.post(link)
        self.state = RedditBotState.READY


    def getLatestMessage(self):
        return self.group.messages().newest


    def getCommands(self):
        commands = self.group.messages(after=self.currentCommand).filter(text__contains=self.prefix+"sr")
        for command in commands:
            if command.id not in self.commandQueue:
                self.commandQueue.append(command)


    def getRandomImage(self, subreddit=None):
        reddit = Reddit("Groupme")
        subImages = []

        if subreddit is None:
            return "None Error"

        try:
            sub = reddit.get_subreddit(subreddit)
            subPosts = sub.get_hot(limit=50)
            if not self.nsfw and sub.over18:
                return "NSFW filter is currently on"
        except errors.PRAWException:
            return str(subreddit) + " is not a valid subreddit"

        for post in subPosts:
            maintype = mimetypes.guess_type(urlparse(post.url).path)[0]
            if maintype in ('image/png', 'image/jpeg', 'image/gif', 'image/jpg'):
               subImages.append(post.url)

        if subImages:
            return random.choice(subImages)
        else:
            return "No images found"


    def setNsfwOn(self):
        self.nsfw = True
        self.bot.post("NSFW ON")
        self.state = RedditBotState.READY


    def setNsfwOff(self):
        self.nsfw = False
        self.bot.post("NSFW OFF")
        self.state = RedditBotState.READY


    def run(self):

        print("Running Bot")
        print("NSFW="+str(self.nsfw))
        print("Admin="+str(self.admin))

        while True:
            try:
                if self.state == RedditBotState.READY:
                    # first make sure queue is empty, if not pop latest command and run it
                    if self.commandQueue:
                        self.state = RedditBotState.BUSY
                        message = self.commandQueue.pop(0)
                        subreddit = message.text.split()[1]
                        if subreddit == "setnsfw" and message.name == self.admin:
                            if "on" in message.text.split()[2]:
                                self.setNsfwOn()
                            if "off" in message.text.split()[2]:
                                self.setNsfwOff()
                        self.currentCommand = str(message.id)
                        self.postImage(subreddit)
                    else:
                        self.getCommands()
                    
                if self.state == RedditBotState.BUSY:
                    self.getCommands()

            except Exception as e:
                print(e)


if __name__ == '__main__':
    bot = RedditBot()
    bot.run()
