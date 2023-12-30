from discord.ext import commands
import discord
from uuid import uuid4
from dataclasses import dataclass, field
from typing import Dict, List
import os

def pad_name(name):
    if len(name) < 15:
        padded_member_name = name + ' ' * (15 - len(name))
    else:
        padded_member_name = name[:15]
    return padded_member_name

@dataclass
class Event:
    title: str = ""
    date: str = ""
    time: str = ""
    channel: str = ""
    banner: str = ""
    team_one: List[str] = field(default_factory=list)
    team_two: List[str] = field(default_factory=list)

    def get_roster(self):
        padding_len = 7
        team_one_padded = [pad_name(name) for name in self.team_one] + ['open'] * (5 - len(self.team_one))
        team_two_padded = [pad_name(name) for name in self.team_two] + ['open'] * (5 - len(self.team_two))

        # Create the roster string
        roster = f"~~{(' ')*padding_len}~~Team 1~~{(' ')*padding_len}~~{(' ')*padding_len}~~{(' ')*padding_len}~~Team 2~~     ~~\n"
        for i, (player_team_one, player_team_two) in enumerate(zip(team_one_padded, team_two_padded), start=1):
            roster += f"{i}. {player_team_one:<15}{(' ' * (12-len(player_team_one)))}{i}. {player_team_two:<15}\n"

        return roster

    
    def add_team_one(self, username):
        if len(self.team_one) < 4:
            self.team_one.append(username)
        else:
            print('roster one full')

    def add_team_two(self, username):
        if len(self.team_two) < 4:
            self.team_two.append(username)
        else:
            print('roster two full')

    def rm_team_one(self, username):
        filtered_list = [name for name in self.team_one if name != username]
        self.team_one = filtered_list

    def rm_team_two(self, username):
        filtered_list = [name for name in self.team_two if name != username]
        self.team_two = filtered_list

    def build_msg(self, event_id):
        msg = f"""
{event_id}
** :star: {self.title} :star:**
~~                                 ~~
**StartTime:** {self.time} {self.date}
**Channel:** {self.channel}
{self.get_roster()}
{self.banner}
"""
        return msg


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
        print('ready')
        self.event_channel = self.bot.get_channel(self.bot.EVENT_CHANNEL)



    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        
        # Get message contents and extract first line
        message = await self.event_channel.fetch_message(payload.message_id)
        member = payload.member
        
        # Get message contents and extract first line
        message_lines = message.content.split('\n')
        first_line = message_lines[0].strip()
        
        if payload.event_type == 'REACTION_ADD' and member.name != self.bot.user.name:
            if member.name in self.users_events[first_line].team_one:
                return
            if member.name in self.users_events[first_line].team_two:
                return
            if payload.emoji.name == '1️⃣':
                self.users_events[first_line].add_team_one(member.name)
                msg = self.users_events[first_line].build_msg(first_line)
                await message.edit(content=msg)
            if payload.emoji.name == '2️⃣':
                self.users_events[first_line].add_team_two(member.name)
                msg = self.users_events[first_line].build_msg(first_line)
                await message.edit(content=msg)
            
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # Get message contents and extract first line
        message = await self.event_channel.fetch_message(payload.message_id)
        
        # This will get the object for the member who owns the reaction that was removed.
        member = discord.utils.get(message.guild.members, id=payload.user_id)
        
        message_lines = message.content.split('\n')
        first_line = message_lines[0].strip()

        if payload.event_type == 'REACTION_REMOVE':
            if payload.emoji.name == '1️⃣':
                self.users_events[first_line].rm_team_one(member.name)
                msg = self.users_events[first_line].build_msg(first_line)
                await message.edit(content=msg)
            if payload.emoji.name == '2️⃣':
                self.users_events[first_line].rm_team_two(member.name)
                msg = self.users_events[first_line].build_msg(first_line)
                await message.edit(content=msg)
            
    
    @commands.Cog.listener()
    async def on_message(self, ctx):
        in_progress = self.in_progress.get(ctx.author.name)
        position = in_progress.get('position')
        event_id = str(in_progress.get('event_id'))

        if str(ctx.channel) == "events" and ctx.author != self.bot.user:
            await ctx.channel.purge(limit=1)
            return

        # Ignore the bots own messages
        if ctx.author == self.bot.user:
            print('bot msg')
        # Ignore non DMs
        if ctx.channel.id != ctx.author.dm_channel.id:
            return
        # Ignore random DMs
        if position is None:
            return
        if ctx.content == "quit" or ctx.content == "exit" or ctx.content == "cancel":
            if self.in_progress.get(ctx.author.name):
                self.in_progress[(ctx.author.name)] = None
            await ctx.author.send("Canceled event creation")
            return
        
        if position == 0:
            self.users_events[event_id] = Event()
            self.users_events[event_id].title = ctx.content
            self.in_progress[ctx.author.name]['position'] = 1
            await ctx.author.send("Date?")

        if position == 1:
            self.users_events[event_id].date = ctx.content
            self.in_progress[ctx.author.name]['position'] = 2
            await ctx.author.send("Time?")
        
        if position == 2:
            self.users_events[event_id].time = ctx.content
            self.in_progress[ctx.author.name]['position'] = 3
            await ctx.author.send("Voice Channel link?")

        if position == 3:
            self.users_events[event_id].channel = ctx.content
            self.in_progress[ctx.author.name]['position'] = 4
            await ctx.author.send("Banner? 'pass' for default banner")
        
        if position == 4:
            if len(ctx.attachments) > 0:
                self.users_events[event_id].banner = ctx.attachments[0].url
                msg = self.users_events[event_id].build_msg(event_id)
                message =  await self.event_channel.send(content=msg)
                await message.add_reaction("1️⃣")
                await message.add_reaction("2️⃣")
                await ctx.author.send("Event created.")

            else:
                file_path = os.path.join('assets', 'Lotus.png')
                self.users_events[event_id].banner = ""
                msg = self.users_events[event_id].build_msg(event_id)

                with open(file_path, 'rb') as f:
                    picture = discord.File(f)
                    os.environ['EVENT_CHANNEL']
                    message = await self.event_channel.send(content=msg, file=picture)
                    await message.add_reaction("1️⃣")
                    await message.add_reaction("2️⃣")
                await ctx.author.send("Event created.")

            self.in_progress[ctx.author.name]['position'] = 5

        
        if position == 5:
            await ctx.author.send("Event already created. Go away. Or send Cashapp donations to $RSkiles614")

        
    @commands.command()
    async def event(self, ctx):
        self.in_progress[ctx.author.name] = {
            "event_id": str(uuid4()),
            "position": 0
        }
        await ctx.author.send("Type 'quit' to abandon event setup")
        await ctx.author.send("Title?")


async def setup(bot):
    await bot.add_cog(EventCommand(bot))
    