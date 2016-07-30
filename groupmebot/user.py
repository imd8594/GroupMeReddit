"""
    Ian Dansereau
    GroupMeReddit
    user.py
    7/30/16

"""


class User(object):

    def __init__(self, user_id, role):
        self._user_id = user_id
        self._role = role

    def getId(self):
        return self._user_id

    def getRole(self):
        return self._role

    def setRole(self, role):
        self._role = role

    def isAdmin(self):
        if self._role == "admin":
            return True
        return False

    def isMod(self):
        if self._role == "moderator":
            return True
        return False

    def isUser(self):
        if self._role == "user":
            return True
        return False

    def isBanned(self):
        if self._role == "banned":
            return True
        return False