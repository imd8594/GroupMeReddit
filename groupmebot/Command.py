"""
    Ian Dansereau
    GroupMeReddit
    command.py
    7/30/16

"""
import mimetypes
import random
from urllib.parse import urlparse
from urllib.request import urlopen

from groupmebot.config import Config
from groupmebot.user import User


class CommandException(Exception):
    def __init__(self, error):
        Exception.__init__(self, "Command Error: " + error)
        self.error = error


class CommandFactory(object):
    def __init__(self, message, bot, reddit, nsfw):
        configs = Config()
        self.admin = configs.admin
        self.moderators = configs.moderators
        self.bannedUsers = configs.banned
        self.nsfw = nsfw
        self.prefix = configs._prefix
        self.adminCommands = ['nsfwfilter', 'ban', 'unban', 'mod', 'unmod']
        self.specialCommands = ['randomsr']
        self.message = message
        self.bot = bot
        self.reddit = reddit
        self.author = None
        self.command = None
        self.commandType = None

        self._setAuthor()
        self._setCommand()

    def getMessage(self):
        return self.message

    def getAuthor(self):
        if self.author is None:
            raise CommandException("Author is None")
        return self.author

    def getCommand(self):
        if self.command is None:
            raise CommandException("Command is None")
        return self.command

    def _setAuthor(self):
        self.role = None
        if self.message.user_id == self.admin:
            self.role = "admin"
        elif self.message.user_id in self.moderators:
            self.role = "moderator"
        elif self.message.user_id in self.bannedUsers:
            self.role = "banned"
        else:
            self.role = "user"

        self.author = User(self.message.user_id, self.role, self.message.name)

    def _setCommand(self):
        try:
            self.command = self.message.text.split(self.prefix + "sr")[1].split()[0].lower()
        except IndexError:
            raise CommandException("Please enter a subreddit or command")

    def createCommand(self):
        if self.command in self.adminCommands:
            if self.command == "nsfwfilter" and "on" in self.message.text.split()[2]:
                return SetNsfwCommand(self.message, self.author, self.bot, True)
            if self.command == "nsfwfilter" and "off" in self.message.text.split()[2]:
                return SetNsfwCommand(self.message, self.author, self.bot, False)
            if self.command == "ban":
                return BanUserCommand(self.message, self.author, self.bot)
            if self.command == "unban":
                return UnBanUserCommand(self.message, self.author, self.bot)
            if self.command == "mod":
                return ModUserCommand(self.message, self.author, self.bot)
            if self.command == "unmod":
                return UnModUserCommand(self.message, self.author, self.bot)
        elif self.command in self.specialCommands:
            if self.command == "randomsr":
                return PostRandomImageCommand(self.message, self.author, self.bot, self.reddit, self.nsfw)
        else:
            return PostImageCommand(self.message, self.author, self.bot, self.reddit, self.command, self.nsfw)


class Command(object):
    def __init__(self, message, author, bot):
        self.configs = Config()
        self.admin = self.configs.admin
        self.moderators = self.configs.moderators
        self.bannedUsers = self.configs.banned
        self.nsfw = self.configs.nsfw
        self.message = message
        self.author = author
        self.bot = bot
        self.id = message.id

    def isValid(self):
        pass

    def run(self):
        pass

    def post(self, post):
        self.bot.post(post)


class PostImageCommand(Command):
    def __init__(self, message, author, bot, reddit, subreddit, nsfw):
        self.reddit = reddit
        self.subreddit = subreddit
        self.nsfw = nsfw
        super().__init__(message, author, bot)

    def getSize(self, url):
        file = urlopen(url)
        size = file.headers.get("content-length")
        if size:
            size = int(size)
        file.close()
        return size / 1000000

    def isValid(self):
        if not self.author.isBanned():
            return True

    def run(self):
        if self.isValid():
            subImages = []
            sub = self.reddit.get_subreddit(self.subreddit)
            if sub.over18 and self.nsfw:
                self.post("NSFW Filter is currently on")
                return
            subPosts = sub.get_hot(limit=50)

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
                print("Error posting an image " + e.__str__())

            if subImages:
                self.post(random.choice(subImages))
            else:
                self.post("No images found")
        else:
            self.post(self.author.getNickname() + " is currently banned")


class PostRandomImageCommand(PostImageCommand):
    def __init__(self, message, author, bot, reddit, nsfw):
        self.nsfw = nsfw
        self.subreddit = str(reddit.get_random_subreddit(self.nsfw))
        super().__init__(message, author, bot, reddit, self.subreddit, nsfw)

    def isValid(self):
        return super().isValid()

    def getSize(self, url):
        return super().getSize(url)

    def run(self):
        super().run()


class BanUserCommand(Command):
    def __init__(self, message, author, bot):
        super().__init__(message, author, bot)

    def isValid(self):
        if not self.author.isBanned():
            if self.author.isAdmin() or self.author.isMod():
                return True
        return False

    def run(self):
        if self.isValid():
            bannedUser = None
            if self.message.attachments:
                for a in self.message.attachments:
                    if a.type == 'mentions':
                        bannedUser = a.user_ids[0]
            else:
                self.post("Please tag a user to ban")
            if bannedUser not in self.bannedUsers:
                self.configs.addBanned(bannedUser)
                self.bannedUsers = self.configs.getBanned()
                self.post(self.author.getNickname() + " banned")
            else:
                self.post(self.author.getNickname() + " is already banned")
        else:
            self.post("Error banning " + self.author.getNickname())


class UnBanUserCommand(BanUserCommand):
    def __init__(self, message, author, bot):
        super().__init__(message, author, bot)

    def isValid(self):
        return super().isValid()

    def run(self):
        if self.isValid():
            bannedUser = None
            if self.message.attachments:
                for a in self.message.attachments:
                    if a.type == 'mentions':
                        bannedUser = a.user_ids[0]
            else:
                self.post("Please tag a user to unban")
            if bannedUser in self.bannedUsers:
                self.configs.removeBanned(bannedUser)
                self.bannedUsers = self.configs.getBanned()
                self.post(self.author.getNickname() + " unbanned")
            else:
                self.post(self.author.getNickname() + " was not banned")
        else:
            self.post("Error unbanning " + self.author.getNickname())


class ModUserCommand(Command):
    def __init__(self, message, author, bot):
        super().__init__(message, author, bot)

    def isValid(self):
        if not self.author.isBanned():
            if self.author.isAdmin():
                return True
        return False

    def run(self):
        if self.isValid():
            modUser = None
            if self.message.attachments:
                for a in self.message.attachments:
                    if a.type == 'mentions':
                        modUser = a.user_ids[0]
            else:
                self.post("Please tag a user to mod")
            if modUser not in self.moderators:
                self.configs.addMod(modUser)
                self.configs.moderators = self.configs.getMods()
                self.post(self.author.getNickname() + " is now a moderator")
            else:
                self.post(self.author.getNickname() + " is already a moderator")
        else:
            self.post("Error modding " + self.author.getNickname())


class UnModUserCommand(ModUserCommand):
    def __init__(self, message, author, bot):
        super().__init__(message, author, bot)

    def isValid(self):
        return super().isValid()

    def run(self):
        if self.isValid():
            modUser = None
            if self.message.attachments:
                for a in self.message.attachments:
                    if a.type == 'mentions':
                        modUser = a.user_ids[0]
            else:
                self.post("Please tag a user to unmod")
            if modUser in self.moderators:
                self.configs.removeMod(modUser)
                self.moderators = self.configs.getMods()
                self.bot.post(self.author.getNickname() + " is no longer a moderator")
            else:
                self.post(self.author.getNickname() + " was not a moderator")
        else:
            self.post("Error Un-modding " + self.author.getNickname())


class SetNsfwCommand(Command):
    def __init__(self, message, author, bot, value):
        self.value = value
        super().__init__(message, author, bot)

    def isValid(self):
        if not self.author.isBanned():
            if self.author.isAdmin() or self.author.isMod():
                return True
        return False

    def run(self):
        if self.isValid():
            if self.value:
                self.configs.setNsfw('on')
                self.post("NSFW Filter on")
            if not self.value:
                self.configs.setNsfw('off')
                self.post("NSFW Filter off")
