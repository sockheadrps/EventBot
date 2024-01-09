import discord
import os
from discord.ext import commands
import asyncio


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    bot.EVENT_CHANNEL = int(os.environ['EVENT_CHANNEL'])


async def load():
    for f in os.listdir("./cogs"):
            if f.endswith(".py"):
                print("cogs." + f[:-3])
                await bot.load_extension(f"cogs.{f[:-3]}")


async def main():
    await load()
    await bot.start(os.environ['TOKEN'])

asyncio.run(main())
