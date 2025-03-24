#___Every Variable Is Mandatory/Required So Fill Those With Causion___#


import logging

#--------------------------------------------------------------------------------------------------------------------------#
# Telegram API credentials
API_ID = "20951184" # Replace with your API_ID 
API_HASH = "33da8f2403e95e6c2504a3c994223c73" # Replace with your HASH
BOT_TOKEN = "8000939036:AAG4QvUuv3F7shFX5EJCJeIdC9rfNWzKuI8" # Replace with your BOT TOKEN
BOT_UN = "Manga3botbot" # Replace with your BOT Username Without @


# MongoDB setup
DB_URL = "mongodb+srv://thakareankit46:<db_password>@comicksect.3gdjj.mongodb.net/?retryWrites=true&w=majority&appName=ComickSect" # Replace with your mongo db url
DB_NAME = "ComickSect" # Do Need To Change This 

# Admin and Channel details
ADMIN = "Letschatbro"  # Replace with your Telegram user ID
CHANNEL = "Manga_Sect" # Replace with your force sub channel username. add bot as admin in yourforce sub channel before start the bot  
DB_CHANNEL_UN = "fuck_umanga"  # Replace with your File store channel username .Must Be Public
IS_NOTIFY = "True"   # "True" or "False". If "True" Then It Will Send New Aired Chapter Notification In DM

# Download directory
DOWNLOAD_DIRECTORY = "./downloads" # Do Need To Change This

# Copyright Banner
BANNER_PATH = "banner.jpg" # Replace with your Copyright Banner Path

#--------------------------------------------------------------------------------------------------------------------------#

# Logging configuration
LOGGING_CONFIG = {  # Do Not Change This
    'level': logging.INFO,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'handlers': [
        logging.FileHandler("manga_bot.log"),
        logging.StreamHandler()
    ]
}
