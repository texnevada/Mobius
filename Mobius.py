# !/usr/bin/python3

# To run this code
# Python 3.8 64bit or higher is required.
# Checks if all requirements are installed. If not it will install them.
import data.functions.ReqInstaller as ReqInstaller
ReqInstaller.check()

# Imports the rest of the modules
import discord
from discord.ext import commands
from discord import app_commands
import logging
import os
import glob
from datetime import date, datetime
import random
from data.functions.owner import is_owner
import data.functions.ConfigSetup as ConfigSetup
import configparser

"""
=========
Config
=========
"""
# Checks to see if the config file exists.
# Will pass if config does exist.
ConfigSetup.check()

# Reads the config and configures parameters.
config = configparser.ConfigParser()
config.read("./config.ini")

APP = config["APP"]

Environment = APP["Environment"]
token = APP["Token"]
Debug = APP["Debug"]
prefix = APP["Prefix"]
boot_msg = APP["Boot_msg"]
ready_msg = APP["Ready_msg"]
bot_name = APP["Bot_Name"]

log_location = config["LOGGING"]["Log"]
log_name = log_location+bot_name+".log"

"""
=========
Logging
=========
"""

if Environment == "Dev":
    print("~~You are running a development version!~~\n"
          "~~It should not be used for production!~~")


if config["LOGGING"]["Logs"] == "True":
    files = glob.glob(log_name)
    now = datetime.now()
    time = now.strftime("%H.%M.%S")
    for file in files:
        split = file.split(".")
        new_name = "{} {} {}.log".format(split[0], date.today(), time)
        try:
            os.rename(file, new_name)
        except:
            new_name = "{} {} {} Random {}.log".format(split[0], date.today(), time, random.randint(1, 10000))
            os.replace(file, new_name)

if Debug == "DEBUG":
    LogLevel = logging.DEBUG
else:
    LogLevel = logging.WARNING

logger = logging.getLogger('discord')
logger.setLevel(LogLevel)
handler = logging.FileHandler(filename=log_name, encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


"""
===========
Prep files
===========
"""


def get_prefix(client, message):
    # if not message.guild:
    #     return commands.when_mentioned_or(*prefix)(client, message)
    return commands.when_mentioned_or(*prefix)(client, message)


intents = discord.Intents.default()
intents.members = eval(APP["Members"])
intents.presences = eval(APP["Presences"])
client = commands.AutoShardedBot(
    command_prefix=get_prefix,
    status=discord.Status.dnd,
    activity=discord.Game(name=boot_msg),
    case_insensitive=eval(APP["Case_insensitive"]),
    # The total number of shards to use between all clusters
    # shard_count=4,
    # Indicate what shard ID to use
    # shard_ids=(0,),
    intents=intents
    )
tree = app_commands.CommandTree(client)
# Here we are deleting the standard help function in discord to make our on in a embed later.
client.remove_command("help")

"""
============================
Slash commands procedure
============================
"""
# tree = app_commands.CommandTree(client)
# # DevGuild = int(APP["DevGuild"])
#
#
# @tree.command(guild=discord.Object(id=int(APP["DevGuild"])))
# async def slash(interaction: discord.Interaction, number: int, string: str):
#     await interaction.response.send_message(f'{number=} {string=}', ephemeral=True)
#
# tree.add_command(slash)
"""
============================
Login procedure for the bot
============================
"""


# will print when the bot has connected to the server
@client.event
async def on_ready():
    # prints that the bot is ready with its username & id
    print(f"\nBot is ready"
          f"\nLogged in as"
          f"\nBot's name: {client.user.name}"
          f"\nBot id: {client.user.id}"
          f"\nDiscord.py version: {discord.__version__}"
          f"\n------"
          f"\nBot is serving: {str(len(client.guilds))} guilds.")
    client.tree = tree
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name=ready_msg))
    if config["LOGGING"]["Logs"] == "False":
        print("[WARN]: Logging is disabled! If this was a mistake. Please enable it in the config under LOGGING.")

# starts a client.event
@client.event
# Defines a fuction when a message is sent
async def on_message(message):
    # Keeps the command in mind when event is running to prevent commands from not working
    await client.process_commands(message)


@client.event
async def on_guild_join(guild):
    # await client.change_presence(status=discord.Status.online, activity=discord.Game(name=">help or @MODUS help"))
    print(f"Bot is serving: {str(len(client.guilds))} guilds.")

# Loads the Cogs Loader
client.load_extension("data.cogs._CogLoader")


"""
============================
Logs the bot out of discord
============================
"""


# logs out the bot from discord
@client.command(name="logout", aliases=["shutdown"])
# User must have the role to continue
@is_owner()
# defines a new function call logout
async def logout(ctx):
    print("\nBot logout requested. Shutting down...\n")
    await ctx.send("Logging out.")
    await client.change_presence(status=discord.Status.invisible)
    # tells the bot to logout
    await client.close()



"""
===========================
This is the end of the client.
===========================
"""

# Checks token to login the bot into discord.
client.run(token, reconnect=True)
