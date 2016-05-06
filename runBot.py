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
    Excepts generic exceptions because catching all the other ones is too much work
"""
def main():
    if not sys.version_info >= (3, 5):
        print("Python 3.5+ is required. This version is %s" % sys.version.split()[0])

    try:
        from groupmebot import RedditBot

        bot = rb()
        bot.run()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
