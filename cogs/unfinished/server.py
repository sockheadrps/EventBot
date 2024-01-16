

from typing import Optional
import discord
from discord.ext import commands
from aiohttp import web
import asyncio


class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles = ""
        self.loop

    @commands.command()
    async def roleinactivity(ctx, role : discord.Role): 
        print(role.members)

    @commands.Cog.listener()
    async def on_ready(self, ctx, role: discord.Role):
        self.roles = "\n".join(str(member) for member in role.members)


async def obs_tts_loop(self):
        connect_event = {
            "event": "CONNECT",
            "client": "TWITCHIO_CLIENT"
        }
        try:
            async with websockets.connect(obs_ws_server) as websocket:
                await websocket.send(json.dumps(connect_event))
                while True:
                    # if speaking Send speaking event to OBS
                    # Random char ID until DB is implemented
                    if self.is_speaking:
                        async with Db("database.sqlite3") as db:
                            # Create table from UserEcon class
                            await db.read_table_schemas(self.bot.UserEcon)
                            find = db.find(self.bot.UserEcon)
                            author = await find(self.user_speaking)
                            if author == None:
                                speaking_event = {
                                    "event": "IS_SPEAKING",
                                    "client": "TWITCHIO_CLIENT",
                                    "user": self.user_speaking,
                                    "level": 0
                                    }
                            else:
                                speaking_event = {
                                    "event": "IS_SPEAKING",
                                    "client": "TWITCHIO_CLIENT",
                                    "user": self.user_speaking,
                                    "level": author.level
                                }
                        await websocket.send(json.dumps(speaking_event))

                        # yeild while speaking
                        while self.is_speaking:
                            await asyncio.sleep(0.1)

                        else:
                            speaking_complete_event = {
                                "event": "SPEAKING_COMPLETE",
                                "client": "TWITCHIO_CLIENT",
                            }
                            await websocket.send(json.dumps(speaking_complete_event))
                    else:
                        await asyncio.sleep(0)

        # Can be connection refused error
        except OSError as e:
            for sub_exception in e.args:
                print('WS connection to OBS/TTS server has been refused')

async def setup(bot):
    await bot.add_cog(Server(bot))


