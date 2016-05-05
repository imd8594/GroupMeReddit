"""
    Ian Dansereau
    $(PROJECT_NAME)
    $(NAME)
    $(DATE)

"""
import sys
from groupmebot.RedditBot import RedditBot as rb

def main():
    if not sys.version_info >= (3, 5):
        print("Python 3.5+ is required. This version is %s" % sys.version.split()[0])

    try:
        from groupmebot import RedditBot

        bot = rb()
        bot.run()

    except Exception as e:
        print(e.__traceback__)


if __name__ == '__main__':
    main()