import discord
from discord.ext import commands
import aiohttp

bot = commands.Bot(command_prefix="!")

async def fetch_roles(guild_id, webhook_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://discord.com/api/guilds/{guild_id}/roles') as response:
            roles_data = await response.json()

            # Process the roles data as needed
            for role in roles_data:
                print(f"Role Name: {role['name']}, Role ID: {role['id']}")

            # Send the roles information to a channel using a webhook
            webhook = discord.Webhook.from_url(webhook_url, adapter=discord.AsyncWebhookAdapter(session))
            await webhook.send("Roles information:\n" + "\n".join([f"Role Name: {role['name']}, Role ID: {role['id']}" for role in roles_data]))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

    # Replace GUILD_ID and WEBHOOK_URL with your actual guild ID and webhook URL
    await fetch_roles(GUILD_ID, WEBHOOK_URL)