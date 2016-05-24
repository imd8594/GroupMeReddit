"""
    Ian Dansereau
    GroupMeReddit
    runBot.py
    5/5/16

"""
import sys
import asyncio
from groupmebot.RedditBot import RedditBot as rb

"""
    Main method
    Excepts generic exceptions because catching all the other ones is too much work
"""


def main():
    if not sys.version_info >= (3, 5):
        print("Python 3.5+ is required. This version is %s" % sys.version.split()[0])

    try:

        bot = rb()
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(bot.run())
        loop.run_forever()
        loop.close()

    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        print(e)
        pass


if __name__ == '__main__':
    main()
