"""
    Ian Dansereau
    GroupMeReddit
    runBot.py
    5/5/16

"""
import sys
from groupmebot.RedditBot import RedditBot as rb

"""
    Main method
"""


def main():
    if not sys.version_info >= (3, 5):
        print("Python 3.5+ is required. This version is %s" % sys.version.split()[0])

    try:

        bot = rb()
        bot.run()

    except Exception as e:
        print(e.__str__())

if __name__ == '__main__':
    main()
