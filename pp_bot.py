import os

import discord
from dotenv import load_dotenv

import pp_comand_parser
import pp_helper
import pp_joke

load_dotenv()


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print("I'm up lets go!")


@client.event
async def on_message(message):
    if message.author == client.user or not message.content.startswith('/pp'):
        return

    result = pp_comand_parser.parse(message.content)

    if type(result) == str:
        await message.channel.send(f"{message.author.mention} Error: {result}")
        return

    (general_flags, general_options, command, command_flags, command_options, others) = result

    if command == 'size':
        if len(others) == 0:
            await message.channel.send(f"{message.author.mention} don't be shy, please provide the pp size")
        else:
            result = pp_joke.judge_pp(float(others[0]))
            await message.channel.send(f"{message.author.mention} {result}")

        return

    url = command
    token = await pp_helper.get_token()
    (_, beatmap_id) = pp_helper.parse_beatmapset_url(url)
    beatmap, attributes = await pp_helper.get_beatmap_data(token, beatmap_id)

    pp = pp_helper.compute_pp(beatmap, attributes)

    beatmapset = beatmap['beatmapset']
    embed = discord.Embed(
        title=f"{beatmapset['artist_unicode']} - {beatmapset['title']}",
        description=f"{beatmapset['play_count']} plays, {beatmapset['favourite_count']} favorites\nMapped by {beatmapset['creator']}\n",
        url=url,
        color=0xFF66AA
    )

    embed.set_thumbnail(url=beatmapset['covers']['list'])
    embed.add_field(name="Max pp:", value=f"~{pp} pp", inline=True)

    await message.channel.send(embed=embed)

PP_BOT_TOKEN = os.environ['PP_BOT_TOKEN']
client.run(PP_BOT_TOKEN)
