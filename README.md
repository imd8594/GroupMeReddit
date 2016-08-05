# GroupMeReddit
Groupme Bot that will randomly post an image from a given subreddit

## Required Python Packages:

		Python Reddit API Wrapper (PRAW): http://praw.readthedocs.io/en/stable/
		GroupyAPI: https://pypi.python.org/pypi/GroupyAPI
		
## How to install:
		1. Clone or download this repository
		
		2. Go to https://dev.groupme.com/ 
		  - Login/create account
		  - Go to https://dev.groupme.com/bots and create a bot
		  - Click "Access Token" in the top right and copy it down for later
		
		3. In your local version of this repository go to the GroupMeReddit/config folder
		  - Open .groupy.key and paste in your Access Token from earlier
		  - Rename example_config.ini to config.ini and change the values to match your 
		    information from http://dev.groupme.com/bots
		    - Change groupid, botid, and adminid to the id's next to your bot
		    **To get adminid you need to run the program once with the current adminid or no adminid
		      and it will list all users in your chat and their id's**
			    
		4. If you don't already have the required packages installed you can run 
		   'pip install -r requirements.txt' inside the GroupMeReddit folder
		
		5. Run the program with python runBot.py
## Usage:

    Admin Commands:
      !sr ban @User
      !sr unban @User
      !sr mod @User
      !sr unmod @User
      !sr nsfwfilter on
      !sr nsfwfilter off

    Moderator Commands:
      !sr ban @User
      !sr unban @User
      !sr nsfwfilter on
      !sr nsfwfilter off

    All User Commands:
      !sr <name_of_subreddit>
      !sr randomsr
