import discord
import os
from discord.ext import commands
import settings

logger = settings.logging.getLogger("bot")


class Bot(commands.Bot):
    def __init__(self) -> None:
        print('Initializing bot')
        logger.info(f"Testing")
        self.EVENT_CHANNEL = int(os.environ['EVENT_CHANNEL'])
        intents = discord.Intents.default()
        intents.message_content=True
        super().__init__(command_prefix="?", intents=intents)


    async def on_ready(self):
        pass
    
    async def setup_hook(self):
        for f in os.listdir("./cogs"):
            if f.endswith(".py"):
                cog_name = f"cogs.{f[:-3]}"
                logger.info(f"Loading cog: {cog_name}")
                await self.load_extension(cog_name)
        
    def run(self) -> None:
        token = os.environ['TOKEN']
        super().run(token)

