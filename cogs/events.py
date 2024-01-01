from discord.ext import commands
import discord
from uuid import uuid4
from dataclasses import dataclass, field
from typing import Dict, List
import os
from datetime import datetime
import logging
import random

def get_random_picture():
    directory_path = 'assets'
    # List all files in the directory
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

    if not files:
        raise FileNotFoundError(f"No files found in the directory: {directory_path}")

    # Randomly select a file
    random_file = random.choice(files)

    # Construct the full file path
    file_path = os.path.join(directory_path, random_file)

    return file_path


log_file_path = 'events.log'
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    channel: str = ""
    banner: str = ""
    team_one: List[str] = field(default_factory=list)
    team_two: List[str] = field(default_factory=list)

    def get_roster(self, team):
        roster = ""
        team_with_open = [pad_name(name) for name in team] + ['open'] * (5 - len(team))
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
        embed = discord.Embed(title=f":star:          {self.title}          :star:", 
                              colour=discord.Colour.dark_magenta())
        
        # Set thumbnial if provided, banner is empty string if we need to set
        file = self.banner
        embed.set_image(url=file)

        if not self.banner:
            file = discord.File(get_random_picture(), filename="output.png")
            embed.set_image(url="attachment://output.png")
        

        embed.add_field(name=f"~~{('-'*48)}~~", value="", inline=False)
        embed.add_field(name=f":waning_crescent_moon: {self.game_type} :waxing_crescent_moon: ", value="", inline=False)
        embed.add_field(name=f":alarm_clock: START TIME {self.date} {self.time} :alarm_clock:", value=f"")
        embed.add_field(name=f":loud_sound: VOICE CHANNEL {self.channel} :loud_sound:", value="", inline=False)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name=f":dog2:~~----~~Team One~~----~~:dog2:", value=self.get_roster(self.team_one))
        embed.add_field(name=f":cat2:~~----~~Team Two~~----~~:cat2:", value=self.get_roster(self.team_two))
        embed.set_footer(text=f"{self.title} created by {self.user}")

        file=None
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

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        
        # Get message contents and user
        message = await self.event_channel.fetch_message(payload.message_id)
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

        
        if payload.event_type == 'REACTION_ADD' and member.name != self.bot.user.name:
            if member.name in self.users_events[event_id].team_one:
                return
            if member.name in self.users_events[event_id].team_two:
                return
            if payload.emoji.name == '1️⃣':
                self.users_events[event_id].add_team_one(member.name)
                embd, _ = self.users_events[event_id].generate_embed()
                await message.edit(embed=embd)
            if payload.emoji.name == '2️⃣':
                self.users_events[event_id].add_team_two(member.name)
                embd, _= self.users_events[event_id].generate_embed()
                await message.edit(embed=embd)
            

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # Get message contents and user
        message = await self.event_channel.fetch_message(payload.message_id)
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
        
        # This will get the object for the member who owns the removed reaction.
        member = discord.utils.get(message.guild.members, id=payload.user_id)

        
        if payload.event_type == 'REACTION_REMOVE':
            if payload.emoji.name == '1️⃣':
                self.users_events[event_id].rm_team_one(member.name)
                embd, _ = self.users_events[event_id].generate_embed()
                await message.edit(embed=embd)
            if payload.emoji.name == '2️⃣':
                self.users_events[event_id].rm_team_two(member.name)
                embd, _= self.users_events[event_id].generate_embed()
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
        
        # If user is making an event, get even creation position and ID
        if in_progress is not None:
            position = in_progress.get('position')
            event_id = in_progress.get('event_id')

        # Quit making an event
        if ctx.content == "quit" or ctx.content == "exit" or ctx.content == "cancel":
            if self.in_progress.get(ctx.author.name):
                self.in_progress[(ctx.author.name)] = None
            await ctx.author.send("Canceled event creation")
            return


        if position is not None:
            match position:
                case 0:
                    event_id = hash(prep_hash(ctx.author.name) + prep_hash(ctx.content))

                    in_progress['event_id'] = event_id
                    self.users_events[event_id] = Event()
                    self.users_events[event_id].user = ctx.author.name
                    self.users_events[event_id].title = ctx.content
                    self.in_progress[ctx.author.name]['position'] = 1
                    await ctx.author.send("What game type?")
                
                case 1:
                    self.users_events[event_id].game_type = ctx.content
                    await ctx.author.send("Date? 'today' to insert todays date")
                    self.in_progress[ctx.author.name]['position'] = 2

                case 2:
                    if ctx.content == "today":
                        current_datetime = datetime.now()
                        formatted_date = current_datetime.strftime("%A, %m/%d/%Y")
                        self.users_events[event_id].date = str(formatted_date)
                        self.in_progress[ctx.author.name]['position'] = 3
                        await ctx.author.send("Time?")
                    else:
                        self.users_events[event_id].date = ctx.content
                        self.in_progress[ctx.author.name]['position'] = 3
                        await ctx.author.send("Time?")
                
                case 3:
                    self.users_events[event_id].time = ctx.content
                    self.in_progress[ctx.author.name]['position'] = 4
                    await ctx.author.send("Voice Channel link?")

                case 4:
                    self.users_events[event_id].channel = ctx.content
                    self.in_progress[ctx.author.name]['position'] = 5
                    await ctx.author.send("Banner? 'pass' for a default banner")
            
                case 5:
                    if len(ctx.attachments) > 0:
                        self.users_events[event_id].banner = ctx.attachments[0].url
                        msg, file = self.users_events[event_id].generate_embed()
                        message =  await self.event_channel.send(embed=msg, file=file)
                        await message.add_reaction("1️⃣")
                        await message.add_reaction("2️⃣")
                        await ctx.author.send("Event created.")

                    else:
                        self.users_events[event_id].banner = ""
                        msg, file = self.users_events[event_id].generate_embed()
                        message = await self.event_channel.send(embed=msg, file=file)
                        await message.add_reaction("1️⃣")
                        await message.add_reaction("2️⃣")
                        await ctx.author.send("Event created.")

                    self.in_progress[ctx.author.name]['position'] = 6

            
                case 6:
                    await ctx.author.send("Event already created. Go away. \
                                        Or send Cashapp donations to $RSkiles614")

        
    @commands.command()
    async def event(self, ctx):
        self.in_progress[ctx.author.name] = {
            "event_id": "",
            "position": 0
        }
        await ctx.author.send("Type 'quit' to abandon event setup")
        await ctx.author.send("Title of Event??")


async def setup(bot):
    await bot.add_cog(EventCommand(bot))
    