import os

import discord

import helper

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print("I'm up lets go!")
    token = await helper.get_token()
    beatmap, attributes = await helper.get_beatmap_data(token)
    r = helper.compute_pp(beatmap, attributes)
    print(r)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/pp'):
        token = await helper.get_token()
        await message.channel.send(token)


PP_BOT_TOKEN = os.environ['PP_BOT_TOKEN']
client.run(PP_BOT_TOKEN)
