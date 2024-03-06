from discord.ext import commands
import discord
from uuid import uuid4
from dataclasses import dataclass, field
from typing import Dict, List
import os
import logging
import random
import asyncio
from .utils.utils import create_event
from discord import app_commands
import time


class Select(discord.ui.Select):
    def __init__(self, roles, guild, name, message, event):
        self.guild = guild
        self.name = name
        self.message = message
        self.event = event
        options = []
        for role in roles:
            if str(role).startswith("CUSTOM"):
                option = discord.SelectOption(
                    label=role.name,
                    emoji="👌",  # You can customize the emoji based on your preferences
                    description=f"Select {role.name} role."
                )
                options.append(option)
        print(options)
        super().__init__(placeholder="Select a role", options=options)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user) == str(self.name):
            # Get the selected role name from values
            selected_role_name = self.values[0]

            # Use discord.utils.get with the guild roles to get the role by name
            selected_role = discord.utils.get(
                self.guild.roles, name=selected_role_name)

            if selected_role:
                self.event.call_roles.append(selected_role)
                msg, file = self.event.generate_embed()
                message = await self.message.edit(embed=msg)
                await interaction.response.defer()

            else:
                await interaction.response.send_message("Invalid role selection.", ephemeral=True)


class SelectView(discord.ui.View):
    def __init__(self, event=None, timeout=20, roles=None, guild=None, name="", message=None):
        super().__init__(timeout=timeout)
        if roles is not None and guild is not None:
            self.add_item(Select(roles, guild, name, message, event))


class Menu(discord.ui.View):
    def __init__(self, event, event_channel, roles=None, guild=None, t_out=0, name=""):
        super().__init__()
        self.value = None
        self.event = event
        self.event_channel = event_channel
        self.roles = roles
        self.guild = guild
        self.t_out = t_out
        self.name = name

    # @discord.ui.button(label="Use default Banner", style=discord.ButtonStyle.green)
    async def create_banner(self, interaction: discord.Interaction):
        msg, file = self.event.generate_embed()

        # file = discord.File(get_random_picture(), filename="output.png")
        file = discord.File('assets/PondGif.gif', filename="output.gif")

        message = await self.event_channel.send(embed=msg, file=file)
        self.event.msg_id = message.id
        await message.add_reaction("1️⃣")
        await message.add_reaction("2️⃣")
        await message.add_reaction("❌")
        await interaction.response.send_message("Choose Roles to alert", view=SelectView(timeout=self.t_out, roles=self.roles, guild=self.guild, name=self.name, event=self.event, message=message), delete_after=self.t_out)

    # @discord.ui.button(label="Use custom banner", style=discord.ButtonStyle.blurple)
    # async def custom(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     await interaction.user.send('Type quit to cancel. Otherwise, attatch IMG file for banner. 1920x1080 seem to work best.')


def get_random_picture():
    directory_path = 'assets'
    # List all files in the directory
    files = [f for f in os.listdir(directory_path) if os.path.isfile(
        os.path.join(directory_path, f))]

    if not files:
        raise FileNotFoundError(
            f"No files found in the directory: {directory_path}")

    # Randomly select a file
    random_file = random.choice(files)

    # Construct the full file path
    file_path = os.path.join(directory_path, random_file)

    return file_path


log_file_path = 'events.log'
logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create the log file or truncate if it exists
with open(log_file_path, 'w'):
    pass


def pad_name(name):
    if len(name) < 15:
        padded_member_name = name + ' ' * (15 - len(name))
    else:
        padded_member_name = name[:15]
    return padded_member_name


def prep_hash(raw_string: str) -> str:
    cleaned_string = raw_string.strip().replace(" ", "")
    return cleaned_string


@dataclass
class Event:
    user: str = ""
    title: str = ""
    game_type = ""
    date: str = ""
    time: str = ""
    time_zone: str = ""
    channel: str = ""
    msg_id: str = ""
    banner: str = ""
    rel_time: str = ""
    team_one: List[str] = field(default_factory=list)
    team_two: List[str] = field(default_factory=list)
    player_ids = []
    roles = []
    call_roles = []

    def get_roster(self, team):
        roster = ""
        team_with_open = [pad_name(name)
                          for name in team] + ['open'] * (5 - len(team))
        for player in team_with_open:
            roster += f"{':small_orange_diamond:'} {player}\n"

        return roster

    def add_team_one(self, username):
        if len(self.team_one) < 4:
            self.team_one.append(username)
        else:
            return

    def add_team_two(self, username):
        if len(self.team_two) < 4:
            self.team_two.append(username)
        else:
            return

    def rm_team_one(self, username):
        filtered_list = [name for name in self.team_one if name != username]
        self.team_one = filtered_list

    def rm_team_two(self, username):
        filtered_list = [name for name in self.team_two if name != username]
        self.team_two = filtered_list

    def generate_embed(self):

        embed = discord.Embed(title=f" ",
                              colour=discord.Colour.dark_magenta())

        # Set thumbnial if provided, banner is empty string if we need to set
        file = self.banner

        if len(self.banner) < 1:
            file = discord.File(get_random_picture(), filename="output.gif")

            embed.set_image(url="attachment://output.gif")
        else:
            embed.set_image(url=file)

        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name=" ", value=" ", inline=False)

        embed.add_field(name=" ", value=" ", inline=True)
        if len(self.title) <= 26:
            embed.add_field(
                name=f":lotus::lotus::lotus:**{self.title}**:lotus::lotus::lotus:", value=" ", inline=False)
        else:
            embed.add_field(
                name=f":lotus::lotus::lotus:**{self.title[:40]}...**:lotus::lotus::lotus:", value=f"{self.title[40:]}", inline=False)

        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name=" ", value=" ", inline=False)

        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(
            name=f":loud_sound:  VOICE CHANNEL{self.channel}  :loud_sound:", value="", inline=True)

        embed.add_field(
            name=f":alarm_clock: {self.rel_time} :alarm_clock:", value=f"", inline=False)
        embed.add_field(name=" ", value="", inline=False)

        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name=" ", value=" ", inline=False)

        embed.add_field(name=f":frog:~~-----~~Team One~~-----~~:frog:",
                        value=self.get_roster(self.team_one))
        embed.add_field(name=f":swan:~~-----~~Team Two~~-----~~:swan:",
                        value=self.get_roster(self.team_two))
        if len(self.call_roles) > 0:
            embed.add_field(name="Roles", value="\n".join(
                [role.mention for role in self.call_roles]), inline=False)
        embed.set_footer(text=f"{self.title} created by {self.user}")

        file = None
        return embed, file


@dataclass
class UsersEvents:
    events: Dict[str, Event]


@dataclass
class CreateInProgres:
    username: str
    event_id: uuid4


class EventCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_events: UsersEvents = {}
        self.in_progress = {}
        self.event_channel = 0

    @commands.Cog.listener()
    async def on_ready(self):
        self.event_channel = self.bot.get_channel(self.bot.EVENT_CHANNEL)
        asyncio.get_event_loop().create_task(self.events_loop())
        # await self.event_channel.purge()
        # await asyncio.sleep(1)
        # await self.event_channel.purge()
        # test_event = create_event(Event)
        # event_id = hash(prep_hash(test_event.user) + prep_hash(test_event.title))
        # self.users_events[event_id] = test_event
        # msg, file = self.users_events[event_id].generate_embed(
        # )

        # message = await self.event_channel.send(embed=msg, file=file)
        # self.users_events[event_id].msg_id = message.id
        # await message.add_reaction("1️⃣")
        # await message.add_reaction("2️⃣")
        # await message.add_reaction("🛠️")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):

        # Get message contents and user
        message = await self.event_channel.fetch_message(payload.message_id)
        if not message:
            return

        member = payload.member
        if not message.embeds:
            return

        embed = message.embeds[0]

        # Extract hash requirements to id the event
        message_lines = embed.footer.text.split('\n')
        first_line = message_lines[0].strip()
        event_creator = first_line.partition(" created by")[2].strip()
        title_of_event = first_line.partition(" created by")[0]

        event_id = hash(prep_hash(event_creator) + prep_hash(title_of_event))

        if not self.users_events.get(event_id):
            return None

        if payload.event_type == 'REACTION_ADD' and member.name != self.bot.user.name:
            if member.name in self.users_events[event_id].team_one:
                return
            if member.name in self.users_events[event_id].team_two:
                return
            self.users_events[event_id].player_ids.append(member)
            if payload.emoji.name == '1️⃣':
                self.users_events[event_id].add_team_one(member.display_name)

                embd, _ = self.users_events[event_id].generate_embed()
                await message.edit(embed=embd)
            if payload.emoji.name == '2️⃣':
                self.users_events[event_id].add_team_two(member.display_name)
                embd, _ = self.users_events[event_id].generate_embed()
                await message.edit(embed=embd)
            if payload.emoji.name == "❌" and member.name == self.users_events[event_id].user:
                del self.users_events[event_id]
                await message.delete()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # Get message contents and user
        if payload.guild_id:
            # Fetch the guild
            guild = self.bot.get_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)
        message = await self.event_channel.fetch_message(payload.message_id)

        if not message or len(message.embeds) < 1:
            return

        embed = message.embeds[0]

        # Extract hash requirements to id the event
        message_lines = embed.footer.text.split('\n')
        first_line = message_lines[0].strip()
        event_creator = first_line.partition(" created by")[2].strip()
        title_of_event = first_line.partition(" created by")[0]

        event_id = hash(prep_hash(event_creator) + prep_hash(title_of_event))
        if not self.users_events.get(event_id):
            return None

        # This will get the object for the member who owns the removed reaction.
        # member = discord.utils.get(message.guild.members, id=payload.user_id)
        print(f"paylload is {member} type {type(member)}")

        if payload.event_type == 'REACTION_REMOVE':
            if payload.emoji.name == '1️⃣':
                self.users_events[event_id].rm_team_one(member.display_name)
                embd, _ = self.users_events[event_id].generate_embed()
                await message.edit(embed=embd)

            if payload.emoji.name == '2️⃣':
                self.users_events[event_id].rm_team_two(member.display_name)
                embd, _ = self.users_events[event_id].generate_embed()
                await message.edit(embed=embd)

    @commands.Cog.listener()
    async def on_message(self, ctx):

        # Check to see if user started making an event
        in_progress = self.in_progress.get(ctx.author.name)
        # If we just started creating an event, or are not creating an event currently
        position = None

        # Delete messages in the event channel
        if str(ctx.channel) == "events" and ctx.author != self.bot.user:
            await ctx.channel.purge(limit=1)
            return

        # Ignore the bots own messages
        if ctx.author == self.bot.user:
            return

        if isinstance(ctx.channel, discord.channel.DMChannel):
            pass
        else:
            return

        # If user is making an event, get even creation position and ID
        if in_progress is not None:
            position = in_progress.get('position')
            event_id = in_progress.get('event_id')
        else:
            return

        # Quit making an event
        if ctx.content == "quit" or ctx.content == "exit" or ctx.content == "cancel":
            if self.in_progress.get(ctx.author.name):
                self.in_progress[(ctx.author.name)] = None
            await ctx.author.send("Canceled event creation")
            return

        if position is not None:
            match position:
                case 0:
                    try:
                        if len(ctx.attachments) > 0:
                            self.users_events[event_id].banner = ctx.attachments[0].url
                            msg, file = self.users_events[event_id].generate_embed(
                            )
                            message = await self.event_channel.send(embed=msg, file=file)
                        self.users_events[event_id].msg_id = message.id
                        await message.add_reaction("1️⃣")
                        await message.add_reaction("2️⃣")
                        await message.add_reaction("❌")
                        await ctx.author.send("Event created.")
                    except Exception as e:
                        await ctx.author.send(f"error {e}")
                        self.in_progress[ctx.author.name]['position'] = 0

    @commands.command()
    async def event(self, ctx):
        self.in_progress[ctx.author.name] = {
            "event_id": "",
            "position": 0
        }
        await ctx.author.send("Type 'quit' to abandon event setup")
        await ctx.author.send("Title of Event??")

    @app_commands.command(name="event", description="Create an event")
    async def Mevent(self, interaction: discord.Interaction, title: str, channel: str, hours_from_now: app_commands.Range[int, 0, 24], minutes_from_now: app_commands.Range[int, 0, 60]):
        await interaction.response.defer()
        name = interaction.user.name
        event_id = hash(prep_hash(name) + prep_hash(title))

        self.users_events[event_id] = Event()
        self.users_events[event_id].user = name
        self.users_events[event_id].title = title
        hours = hours_from_now
        minutes = minutes_from_now
        self.seconds = ((hours * 60) + minutes) * 60

        future_timestamp = time.time() + ((hours * 60) + minutes) * 601
        self.users_events[event_id].time = future_timestamp
        discord_timestamp = f"<t:{int(future_timestamp)}:R>"
        self.users_events[event_id].rel_time = discord_timestamp

        self.users_events[event_id].channel = channel

        event = self.users_events[event_id]
        chan = self.bot.get_channel(self.bot.EVENT_CHANNEL)
        for guild in self.bot.guilds:
            g = guild
            for role in await guild.fetch_roles():
                if str(role).startswith("CUSTOM"):
                    self.users_events[event_id].roles.append(role)
        view = Menu(
            event, chan, self.users_events[event_id].roles, g, self.seconds, name)
        await view.create_banner(interaction)
        self.in_progress[name] = {
            "event_id": event_id,
            "position": 0
        }
        try:
            # Send the initial response
            await interaction.followup.send(content=discord_timestamp, ephemeral=True, view=view)
            # await interaction.response.send_message(content=discord_timestamp, ephemeral=True, view=view)
        except discord.errors.InteractionResponded:
            # If the interaction has already been responded to, log the error or handle it accordingly
            print("Interaction has already been responded to.")

    async def events_loop(self):
        reminder_delay = 120
        clean_up_delay = 300
        reminder = True
        starting = True

        while True:
            events_to_remove = []

            for evt_id, evt in self.users_events.items():
                # Reminder
                if (evt.time - reminder_delay < time.time()) and reminder:
                    mention_strings = [
                        f"<@{member.id}>" for member in evt.player_ids]
                    mention_string = ' '.join(mention_strings)
                    a_to_del = await self.event_channel.send(f"Hey {mention_string}, there's an event happening in {evt.rel_time}, {evt.title} with {evt.user}")
                    reminder = False
                if (evt.time < time.time()) and starting:
                    mention_strings = [
                        f"<@{member.id}>" for member in evt.player_ids]
                    mention_string = ' '.join(mention_strings)
                    to_del = await self.event_channel.send(f"Hey {mention_string}, {evt.title} happening now!")
                    starting = False
                if (evt.time + clean_up_delay < time.time()):
                    events_to_remove.append(evt_id)
                    delete_event = await self.event_channel.fetch_message(evt.msg_id)
                    await delete_event.delete()
                    await a_to_del.delete()
                    await to_del.delete()

            for evt_id in events_to_remove:
                del self.users_events[evt_id]

            await asyncio.sleep(1)


async def setup(bot):
    await bot.add_cog(EventCommand(bot))
