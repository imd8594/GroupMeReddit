"""
    Ian Dansereau
    GroupMeReddit
    user.py
    7/30/16

"""

class User(object):

    def __init__(self, id, role):
        self.id = id
        self.role = role

    def getId(self):
        return self.id

    def getRole(self):
        return self.role

    def setRole(self, role):
        self.role = role

    def isAdmin(self):
        if self.role == "admin":
            return True
        return False

    def isMod(self):
        if self.role == "moderator":
            return True
        return False

    def isUser(self):
        if self.role == "user":
            return True
        return False

    def isBanned(self):
        if self.role == "banned":
            return True
        return False