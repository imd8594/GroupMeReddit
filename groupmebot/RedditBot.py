"""
    Ian Dansereau
    GroupMeReddit
    RedditBot.py
    5/5/16

"""
import mimetypes
import random
import traceback
import asyncio
from urllib.parse import urlparse
from urllib.request import urlopen
from collections import OrderedDict

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
        self.commandQueue = OrderedDict()


    def getLatestMessage(self):
        return self.group.messages().newest


    async def getCommands(self):
        commands = self.group.messages(after=self.currentCommand).filter(text__contains=self.prefix+"sr")
        for command in commands:
            if command.id not in self.commandQueue.values():
                self.commandQueue[command] = command.id



    async def postRandomImage(self, subreddit=None):
        reddit = Reddit("Groupme")
        subImages = []
        subPosts = []

        if subreddit is None:
            self.bot.post("None Error")
            self.state = RedditBotState.READY

        try:
            sub = reddit.get_subreddit(subreddit)
            subPosts = sub.get_hot(limit=50)
            if not self.nsfw and sub.over18:
                self.bot.post("NSFW filter is currently on")
                self.state = RedditBotState.READY
        except errors.PRAWException:
            self.bot.post(str(subreddit) + " is not a valid subreddit")
            self.state = RedditBotState.READY

        try:
            for post in subPosts:
                imageExt = ['.jpg', '.jpeg','.png']
                gifExt = ['.gif', '.gifv']
                mimetype = mimetypes.guess_type(urlparse(post.url).path)[0]
                if mimetype in ('image/png', 'image/jpg') or post.url.endswith(tuple(imageExt)):
                    subImages.append(post.url)
                if mimetype in ('image/gif', '') or post.url.endswith(tuple(gifExt)):
                    if self.getSize(post.url) < 10:
                        subImages.append(post.url)
        except Exception as e:
            print(e)

        if subImages:
            self.bot.post(random.choice(subImages))
            self.state = RedditBotState.READY
        else:
            self.bot.post("No images found")
            self.state = RedditBotState.READY

    async def runCommand(self):
        self.state = RedditBotState.BUSY
        message = self.commandQueue.popitem(0)[0]
        subreddit = message.text.split(self.prefix+"sr")[1].split()[0]
        if subreddit == "setnsfw" and message.name == self.admin:
            if "on" in message.text.split()[2]:
                self.setNsfwOn()
            if "off" in message.text.split()[2]:
                self.setNsfwOff()
        self.currentCommand = str(message.id)
        await self.postRandomImage(subreddit)

    def getSize(self, url):
        file = urlopen(url)
        size = file.headers.get("content-length")
        if size:
            size = int(size)
        file.close()
        return size/1000000

    def setNsfwOn(self):
        self.nsfw = True
        self.bot.post("NSFW Filter off")
        self.state = RedditBotState.READY


    def setNsfwOff(self):
        self.nsfw = False
        self.bot.post("NSFW Filter on")
        self.state = RedditBotState.READY


    async def run(self):

        print("Running Bot")
        print("NSFW="+str(self.nsfw))
        print("Admin="+str(self.admin))

        while True:
            try:
                if self.state == RedditBotState.READY:
                    if len(self.commandQueue) > 0:
                        await self.runCommand()
                    else:
                        await self.getCommands()

                if self.state == RedditBotState.BUSY:
                    await self.getCommands()

            except Exception as e:
                print(traceback.print_tb(e.__traceback__))


if __name__ == '__main__':
    bot = RedditBot()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.run().send(None))
    loop.close()
