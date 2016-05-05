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

        self.bannedUsers = []

        self.bot = [bot for bot in Bot.list() if bot.bot_id == self.botID][0]


    def postImage(self, subreddit=None):
        link = self.getRandomImage(subreddit)
        self.bot.post(link)


    def getLatestMessage(self):
        return [group for group in Group.list() if group.group_id == self.groupID][0].messages().newest


    def getRandomImage(self, subreddit=None):
        reddit = Reddit("Groupme")
        subImages = []

        if subreddit is None:
            return "None Error"

        try:
            sub = reddit.get_subreddit(subreddit)
            subPosts = sub.get_hot(limit=40)
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


    def banUser(self, username):
        self.bannedUsers.append(username)


    def unbanUser(self, username):
        self.bannedUsers.remove(username)


    def setNsfwOn(self):
        self.nsfw = True
        self.bot.post("NSFW ON")


    def setNsfwOff(self):
        self.nsfw = False
        self.bot.post("NSFW OFF")


    def run(self):

        print("Running Bot")
        print("NSFW="+str(self.nsfw))
        print("Admin="+str(self.admin))

        while True:
            try:
                message = self.getLatestMessage()
                messageText = message.text.lower()
                messageAuthor = message.name

                if self.prefix + "set ban" in messageText and messageAuthor == self.admin:
                     self.banUser(messageText.split(self.prefix+"set ban")[1])
                if self.prefix + "set unban" in messageText and messageAuthor == self.admin:
                     self.unbanUser(messageText.split(self.prefix+"sr ban")[1])
                if self.prefix + "set nsfw" in messageText and messageAuthor == self.admin:
                    if "on" in messageText.split(self.prefix+"set nsfw")[1]:
                        self.setNsfwOn()
                    if "off" in messageText.split(self.prefix+"set nsfw")[1]:
                        self.setNsfwOff()
                elif self.prefix + "sr" in messageText:
                    if messageAuthor not in self.bannedUsers:
                        subreddit = messageText.split(self.prefix+"sr")[1].split()[0]
                        self.postImage(subreddit)

            except Exception as e:
                print(e)


if __name__ == '__main__':
    bot = RedditBot()
    bot.run()
