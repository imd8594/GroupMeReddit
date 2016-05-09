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
from groupy.api.errors import ApiError
from praw import Reddit, errors

from groupmebot.config import Config

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

        self.currentCommand = str(self.getLatestMessage().id)
        self.commandQueue = OrderedDict()
        self.bannedUsers = []

    def getLatestMessage(self):
        return self.group.messages().newest

    def connectBot(self):
        self.bot = [bot for bot in Bot.list() if bot.bot_id == self.botID][0]
        self.group = [group for group in Group.list() if group.group_id == self.groupID][0]

    def getCommands(self):
        try:
            commands = self.group.messages(after=self.currentCommand).filter(text__contains=self.prefix + "sr")
            for command in commands:
                if command.id not in self.commandQueue.values():
                    self.commandQueue[command] = command.id
        except ApiError as e:
            self.connectBot()
            print(print(traceback.print_tb(e.__traceback__)))

    async def postRandomImage(self, subreddit=None):
        reddit = Reddit("Groupme")
        subImages = []
        subPosts = []

        if subreddit is None:
            self.bot.post("None Error")

        try:
            sub = reddit.get_subreddit(subreddit)
            subPosts = sub.get_hot(limit=50)
            if not self.nsfw and sub.over18:
                self.bot.post("NSFW filter is currently on")
                return
        except errors.PRAWException:
            self.bot.post(str(subreddit) + " is not a valid subreddit")
            return

        try:
            for post in subPosts:
                imageExt = ['.jpg', '.jpeg', '.png']
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
        else:
            self.bot.post("No images found")

    async def runCommand(self):
        message = self.commandQueue.popitem(0)[0]
        self.currentCommand = str(message.id)
        if message.user_id not in self.bannedUsers:
            subreddit = message.text.split(self.prefix + "sr")[1].split()[0]
            if subreddit == "setnsfw" and message.user_id == self.admin:
                if "on" in message.text.split()[2]:
                    self.setNsfwOn()
                if "off" in message.text.split()[2]:
                    self.setNsfwOff()
                return
            if subreddit == "ban" and message.user_id == self.admin:
                if message.attachments:
                    for a in message.attachments:
                        if a.type == 'mentions':
                            bannedUser = a.user_ids[0]
                    self.banUser(bannedUser)
                else:
                    self.bot.post("Please tag a user to ban")
                return
            if subreddit == "unban" and message.user_id == self.admin:
                if message.attachments:
                    for a in message.attachments:
                        if a.type == 'mentions':
                            unbannedUser = a.user_ids[0]
                    self.unbanUser(unbannedUser)
                else:
                    self.bot.post("Please tag a user to unban")
                return
            await self.postRandomImage(subreddit)
        else:
            self.bot.post(message.name + " is currently banned")

    def getSize(self, url):
        file = urlopen(url)
        size = file.headers.get("content-length")
        if size:
            size = int(size)
        file.close()
        return size / 1000000

    def banUser(self, userID):
        user = [member for member in self.group.members() if member.user_id == userID][0]
        if user is not None:
            self.bannedUsers.append(user.user_id)
            self.bot.post(user.nickname + " banned")
        else:
            self.bot.post("Error Banning " + user.nickname)

    def unbanUser(self, userID):
        user = [member for member in self.group.members() if member.user_id == userID][0]
        if user.user_id in self.bannedUsers:
            self.bannedUsers.remove(user.user_id)
            self.bot.post(user.nickname + " un-banned")
        else:
            self.bot.post("Error Un-banning " + user.nickname)

    def setNsfwOn(self):
        self.nsfw = True
        self.bot.post("NSFW Filter off")

    def setNsfwOff(self):
        self.nsfw = False
        self.bot.post("NSFW Filter on")

    async def run(self):

        print("Running Bot")
        print("NSFW=" + str(self.nsfw))
        print("Admin=" + str([member for member in self.group.members() if member.user_id == self.admin][0]))

        while True:
            try:
                if self.commandQueue:
                    await self.runCommand()
                else:
                    self.getCommands()

            except Exception as e:
                self.connectBot()
                print(traceback.print_tb(e.__traceback__))


if __name__ == '__main__':
    bot = RedditBot()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.run().send(None))
    loop.close()
