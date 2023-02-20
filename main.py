# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import discord 
import re
from discord.ext import commands
import os

async def dm_about_roles(member):
    print(f"DMing {member.name}...")

    await member.send(
        f"""Хей {member.name}, добре дошъл!

  Избери си какво икскаш да вършиш:

* общак (🛐)
* хамал (🏋️)
* регистрация (📖)
* информация (ℹ️)
* храна (🍕)
* фотограф (📸)

Можеш да отговориш на съобщението както и с текст, така и с емоджита, за да получите една или повече роли в сървъра. 

P.S много лудо, че сте доброволци!
"""
    )

intents=discord.Intents.all()
client = commands.Bot(command_prefix='!',intents=intents)
SERVER_ID = os.getenv("SERVER")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    guild = client.guilds[0]
    print(guild.roles)

@client.event
async def on_member_join(member):
    await dm_about_roles(member)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')

    if message.content.startswith("!roles"):
        await dm_about_roles(message.author)

async def assign_roles(message):
    print("Assigning roles...")

    languages = set(re.findall("общак|хамал|регистрация|информация|храна|фотограф", message.content, re.IGNORECASE))
    language_emojis = set(re.findall("\U0001F6D0|\U0001F3CB|\U0001F4D6|\U00002139|\U0001F355|U0001F4F8|az sum shefut ei", message.content))
    # https://unicode.org/emoji/charts/full-emoji-list.html
  
    # Convert emojis to names
    for emoji in language_emojis:
        {
            "\U0001F6D0": lambda: languages.add("общак"),
            "\U0001F3CB": lambda: languages.add("хамал"),
            "\U0001F4D6": lambda: languages.add("регистрация"),
            "\U00002139": lambda: languages.add("информация"),
            "\U0001F355": lambda: languages.add("храна"),
            "\U0001F4F8": lambda: languages.add("фотограф"),
            "az sum shefut ei": lambda: languages.add("Организатор")
        }[emoji]()
    if languages:
        print(SERVER_ID)
        server = client.get_guild(int(SERVER_ID))
        print(server)

        print(languages)
        roles = [discord.utils.get(server.roles, name=language) for language in languages]

        member = await server.fetch_member(message.author.id)
        try:
            await member.add_roles(*roles, reason="Сложихме ти роли")
        except Exception as e:
            print(e)
            await message.channel.send("Нещо се обърка, свържи се ")
        else:
            await message.channel.send(f"""Йееееей, вече си { ', '.join(languages) } в {server.name}!""")
    else:
        await message.channel.send("ъъъъъм, такава роля не съществува")

@client.event
async def on_message(message):
    print("Saw a message...")

    if message.author == client.user:
        return # prevent responding to self

    # NEW CODE BELOW
    # Assign roles from DM
    if isinstance(message.channel, discord.channel.DMChannel):
        await assign_roles(message)
        return
    # NEW CODE ABOVE

    # Respond to commands
    if message.content.startswith("!roles"):
        await dm_about_roles(message.author)
    elif message.content.startswith("!serverid"):
        await message.channel.send(message.channel.guild.id)

try:
    client.run(os.getenv("TOKEN"))
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
        print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
    else:
        raise e