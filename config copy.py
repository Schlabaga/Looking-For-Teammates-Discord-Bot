import pymongo
from discord.ext import commands
import discord

MONGO_CLIENT_KEY = "MONGODB KEY"

MongoClient = pymongo.MongoClient(MONGO_CLIENT_KEY)
dbUser = MongoClient.userconfig
dbBot = MongoClient.botconfig
dbServer = MongoClient.serverconfig



bot = commands.Bot(command_prefix="+", intents= discord.Intents.all())
TOKEN="TOKEN"
