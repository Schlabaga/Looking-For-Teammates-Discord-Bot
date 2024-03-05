import pymongo
from discord.ext import commands
import discord
import os
from dotenv import load_dotenv

load_dotenv()


MONGO_CLIENT_KEY = os.getenv('MONGO_CLIENT_KEY')
TOKEN = os.getenv('TOKEN')

MongoClient = pymongo.MongoClient(MONGO_CLIENT_KEY)
dbUser = MongoClient.userconfig
dbBot = MongoClient.botconfig
dbServer = MongoClient.serverconfig

bot = commands.Bot(command_prefix="+", intents= discord.Intents.all())


ranks = {
    "iron1": "1214624515183869953",
    "iron2": "",
    "iron3": "",
    "bronze1": "",
    "bronze2": "",
    "bronze3": "",
    "silver1": "",
    "silver2": "",
    "silver3": "",
    "gold1": "",
    "gold2": "",
    "gold3": "",
    "platinum1": "",
    "platinum2": "",
    "platinum3": "",
    "diamond1": "",
    "diamond2": "",
    "diamond3": "",
    "ascendant1": "",
    "ascendant2": "",
    "ascendant3": "",
    "immortal1": "",
    "immortal2": "",
    "immortal3": "",
    "radiant": ""
}