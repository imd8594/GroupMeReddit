"""
    Ian Dansereau
    GroupMeReddit
    RedditBot.py
    5/5/16

"""
import mimetypes
import random
import traceback
from collections import OrderedDict
from urllib.parse import urlparse
from urllib.request import urlopen

from groupy import Group, Bot, config
from groupy.api.errors import ApiError
from praw import Reddit, errors

from groupmebot.config import Config


def getSize(url):
    file = urlopen(url)
    size = file.headers.get("content-length")
    if size:
        size = int(size)
    file.close()
    return size / 1000000


"""
    Bot object that will get a random image from a subreddit and post it to groupme

"""


class RedditBot(object):
    def __init__(self):
        configs = Config()
        config.KEY_LOCATION = configs.api_key

        self.config = configs

        self.admin = configs.admin
        self.moderators = configs.moderators
        self.bannedUsers = configs.banned
        self.groupID = configs._groupID
        self.botID = configs._botID
        self.prefix = configs._prefix
        self.nsfw = configs.nsfw
        self.reddit = Reddit("Groupme")

        self.bot = [bot for bot in Bot.list() if bot.bot_id == self.botID][0]
        self.group = [group for group in Group.list() if group.group_id == self.groupID][0]

        self.currentCommand = str(self.getLatestMessage().id)
        self.commandQueue = OrderedDict()

    def getLatestMessage(self):
        return self.group.messages().newest

    def connectBot(self):
        self.bot = [bot for bot in Bot.list() if bot.bot_id == self.botID][0]
        self.group = [group for group in Group.list() if group.group_id == self.groupID][0]

    def getCommands(self):
        try:
            if len(self.group.messages(after=self.currentCommand).filter(text__contains=self.prefix + "sr")) > 0:
                commands = self.group.messages(after=self.currentCommand).filter(text__contains=self.prefix + "sr")
                for command in commands:
                    if command.id not in self.commandQueue.values():
                        self.commandQueue[command] = command.id
        except Exception as e:
            self.connectBot()
            print(e)
            print(print(traceback.print_tb(e.__traceback__)))

    async def filterCommands(self):
        command = self.commandQueue.popitem(0)[0]
        self.currentCommand = command.id
        nonPostCommands = ['setnsfw', 'ban', 'unban', 'mod', 'unmod']

        if command.user_id not in self.bannedUsers:
            subreddit = command.text.split(self.prefix + "sr")[1].split()[0].lower()
            if subreddit in nonPostCommands:
                if subreddit == "setnsfw" and (command.user_id == self.admin or command.user_id in self.moderators):
                    if "on" in command.text.split()[2]:
                        await self.setNsfw(True)
                    if "off" in command.text.split()[2]:
                        await self.setNsfw(False)
                    return

                if subreddit == "ban" and (command.user_id == self.admin or command.user_id in self.moderators):
                    if command.attachments:
                        for a in command.attachments:
                            if a.type == 'mentions':
                                bannedUser = a.user_ids[0]
                        if bannedUser != self.admin and bannedUser not in self.moderators:
                            await self.banUser(bannedUser)
                        else:
                            self.bot.post("Cannot ban admin or moderator")
                    else:
                        self.bot.post("Please tag a user to ban")
                    return

                if subreddit == "unban" and (command.user_id == self.admin or command.user_id in self.moderators):
                    if command.attachments:
                        for a in command.attachments:
                            if a.type == 'mentions':
                                unbannedUser = a.user_ids[0]
                        await self.unbanUser(unbannedUser)
                    else:
                        self.bot.post("Please tag a user to unban")
                    return

                if subreddit == "mod" and command.user_id == self.admin:
                    if command.attachments:
                        for a in command.attachments:
                            if a.type == 'mentions':
                                moddedUser = a.user_ids[0]
                        await self.modUser(moddedUser)
                    else:
                        self.bot.post("Please tag a user to mod")
                    return

                if subreddit == "unmod" and command.user_id == self.admin:
                    if command.attachments:
                        for a in command.attachments:
                            if a.type == 'mentions':
                                unModdedUser = a.user_ids[0]
                        await self.unmodUser(unModdedUser)
                    else:
                        self.bot.post("Please tag a user to unban")
                    return
            else:

                try:
                    if subreddit == "randomsr":
                        sub = self.reddit.get_random_subreddit(self.nsfw)
                    else:
                        sub = self.reddit.get_subreddit(subreddit)
                    if not self.nsfw and sub.over18:
                        self.bot.post("NSFW filter is currently on")
                        return
                    await self.postRandomImage(sub)
                except errors.PRAWException:
                    self.bot.post(str(subreddit) + " is not a valid subreddit")
                    return
        else:
            self.bot.post(command.name + " is currently banned")

    async def postRandomImage(self, subreddit):
        subImages = []
        subPosts = subreddit.get_hot(limit=50)

        if subreddit is None:
            self.bot.post("None Error")

        try:
            for post in subPosts:
                imageExt = ['.jpg', '.jpeg', '.png']
                gifExt = ['.gif', '.gifv']
                mimetype = mimetypes.guess_type(urlparse(post.url).path)[0]
                if mimetype in ('image/png', 'image/jpg') or post.url.endswith(tuple(imageExt)):
                    subImages.append(post.url)
                if mimetype in ('image/gif', '') or post.url.endswith(tuple(gifExt)):
                    if getSize(post.url) < 10:
                        subImages.append(post.url)
        except Exception as e:
            print(e)

        if subImages:
            self.bot.post(random.choice(subImages))
        else:
            self.bot.post("No images found")

    async def banUser(self, userID):
        user = [member for member in self.group.members() if member.user_id == userID][0]
        if user is not None:
            if userID not in self.bannedUsers:
                self.config.addBanned(user.user_id)
                self.bannedUsers = self.config.getBanned()
                self.bot.post(user.nickname + " banned")
            else:
                self.bot.post(user.nickname + " is already banned")
        else:
            self.bot.post("Error Banning " + user.nickname)

    async def unbanUser(self, userID):
        user = [member for member in self.group.members() if member.user_id == userID][0]
        if user.user_id in self.bannedUsers:
            self.config.removeBanned(user.user_id)
            self.bannedUsers = self.config.getBanned()
            self.bot.post(user.nickname + " un-banned")
        else:
            self.bot.post("Error Un-banning " + user.nickname)

    async def modUser(self, userID):
        user = [member for member in self.group.members() if member.user_id == userID][0]
        if user is not None:
            if userID not in self.moderators:
                self.config.addMod(user.user_id)
                self.moderators = self.config.getMods()
                self.bot.post(user.nickname + " is now a moderator")
            else:
                self.bot.post(user.nickname + " is already a moderator")
        else:
            self.bot.post("Error Modding " + user.nickname)

    async def unmodUser(self, userID):
        user = [member for member in self.group.members() if member.user_id == userID][0]
        if user.user_id in self.moderators:
            self.config.removeMod(user.user_id)
            self.moderators = self.config.getMods()
            self.bot.post(user.nickname + " is no longer a moderator")
        else:
            self.bot.post("Error Un-Modding " + user.nickname)

    async def setNsfw(self, value):
        if value:
            self.nsfw = True
            self.bot.post("NSFW Filter off")
        if not value:
            self.nsfw = False
            self.bot.post("NSFW Filter on")

    async def run(self):

        print("Running Bot")
        print("NSFW=" + str(self.nsfw))
        print("Admin=" + str([member for member in self.group.members() if member.user_id == self.admin][0]))

        while True:
            try:
                if self.commandQueue:
                    await self.filterCommands()
                else:
                    self.getCommands()

            except Exception as e:
                self.connectBot()
                print(traceback.print_tb(e.__traceback__))
