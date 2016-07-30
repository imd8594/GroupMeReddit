"""
    Ian Dansereau
    GroupMeReddit
    Command
    7/30/16

"""
from groupmebot.config import Config

class CommandException(Exception):
    def __init__(self, error):
        Exception.__init__(self,"Command Error: " + error)
        self.error = error


class Command(object):

    def __init__(self, message):
        configs = Config()
        self._admin = configs.admin
        self._moderators = configs.moderators
        self._bannedUsers = configs.banned
        self._adminCommands = ['setnsfw', 'ban', 'unban', 'mod', 'unmod']
        self.message = message
        self.id = message.id
        self.author = message.user_id
        self.command = None
        self.commandType = None
        self.role = None

        self._setCommand()
        self._setCommandType()
        self._setRole()

    def getMessage(self):
        return self.message

    def getId(self):
        return self.id

    def getAuthor(self):
        return self.author

    def getCommand(self):
        if self.command is None:
            raise CommandException("Command is None")
        return self.command

    def getCommandType(self):
        if self.commandType is None:
            raise CommandException("Command Type is None")
        return self.commandType

    def getRole(self):
        if self.role is None:
            raise CommandException("Role is None")
        return self.role

    def _setRole(self):
        if self.author == self._admin:
            self.role = "admin"
        if self.author in self._moderators:
            self.role = "moderator"
        if self.author in self._bannedUsers:
            self.role = "banned"
        else:
            self.role = "user"

    def _setCommand(self):
        try:
            self.command = self.messsage.text.split(self.prefix + "sr")[1].split()[0].lower()
            self._setCommandType()
        except IndexError:
            raise CommandException("Please enter a subreddit or command")

    def _setCommandType(self):
        if self.command in self._adminCommands:
            self.commandType = "admin"
        else:
            self.commandType = "user"

    def isValidCommand(self):
        if self.command is not None and self.commandType is not None and self.role is not None:
            if self.commandType == "admin" and self.role in ["admin", "moderator"]:
                return True
            if self.commandType == "user" and self.role != "banned":
                return True
        else:
            raise CommandException("Command is not valid")



