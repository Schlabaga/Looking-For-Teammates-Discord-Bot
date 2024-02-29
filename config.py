import pymongo
from discord.ext import commands
import discord
import os
from dotenv import load_dotenv

load_dotenv()


MONGO_CLIENT_KEY = os.getenv('MONGO_CLIENT_KEY')
TOKEN = os.getenv('TOKEN')
print(TOKEN)

MongoClient = pymongo.MongoClient(MONGO_CLIENT_KEY)
dbUser = MongoClient.userconfig
dbBot = MongoClient.botconfig
dbServer = MongoClient.serverconfig

bot = commands.Bot(command_prefix="+", intents= discord.Intents.all())
