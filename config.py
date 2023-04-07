import pymongo
from discord.ext import commands
import discord
import os

MONGO_CLIENT_KEY = os.environ.get('MONGO_CLIENT_KEY')
TOKEN = os.environ.get('TOKEN')

MongoClient = pymongo.MongoClient(MONGO_CLIENT_KEY)
dbUser = MongoClient.userconfig
dbBot = MongoClient.botconfig
dbServer = MongoClient.serverconfig

bot = commands.Bot(command_prefix="+", intents= discord.Intents.all())
