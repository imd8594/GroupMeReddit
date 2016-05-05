"""
    Ian Dansereau
    $(PROJECT_NAME)
    $(NAME)
    $(DATE)

"""
import configparser


class Config(object):
    def __init__(self):

        self.config_file = 'config/config.ini'
        self.api_key = 'config/.groupy.key'

        config = configparser.ConfigParser()
        config.read(self.config_file, encoding='utf-8')

        self._groupID = config.get('BOT', 'GroupID', fallback=None)
        self._botID = config.get('BOT', 'BotID', fallback=None)
        self._prefix = config.get('BOT', 'Prefix', fallback='!')

        self.admin = config.get('ADMIN', 'Admin', fallback=None)
        self.nsfw = config.getboolean('ADMIN', 'Nsfw', fallback=False)

