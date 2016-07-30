"""
    Ian Dansereau
    GroupMeReddit
    Command
    7/30/16

"""


class Command(object):

    def __init__(self, author, type, subreddit, admin, moderators):
        self.author = author
        self.type = type
        self.subreddit = subreddit
        self.role = None

        self._admin = admin
        self._moderators = moderators

    def getAuthor(self):
        return self.author

    def getType(self):
        return self.type

    def getSubreddit(self):
        return self.subreddit

    def getRole(self):
        if self.role is None:
            self.setRole()
        return self.role

    def _setRole(self):
        if self.author == self._admin:
            self.role = "admin"
        if self.author in self._moderators:
            self.role = "moderator"
        else:
            self.role = "user"




