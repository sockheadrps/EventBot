from discord.ext import commands
import discord
from uuid import uuid4
from dataclasses import dataclass, field
from typing import Dict, List
import os
from datetime import datetime, timezone, timedelta
import logging
import random
import asyncio
import pytz
from zoneinfo import ZoneInfo
from .utils.utils import create_event

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

timezone_dict = {
    "HST": "-10",
    "AKST": "-9",
    "PST": "-8",
    "MST": "-7",
    "CST": "-6",
    "EST": "-5"
}


def convert_user_input_to_utc(user_input, utc_offset):
    user_time = user_input
    try:
        # Parse user input as a time
        user_time = datetime.strptime(user_input, "%I:%M%p")  # For 12-hour format like 4:30PM
    except ValueError:
        try:
            # If the first attempt fails, try parsing as 24-hour format like 14:30
            user_time = datetime.strptime(user_input, "%H:%M")
        except ValueError:
            # If both attempts fail, handle the error (invalid input)
            return None

    # Format the time as AM/PM
    formatted_time = user_time.strftime('%I:%M%p')

    return formatted_time


def convert_user_time_to_utc(usr_time, usr_timezone):
    try:
        # Parse user input as a time
        user_time = datetime.strptime(usr_time, "%I:%M%p")  # For 12-hour format like 4:30PM
    except ValueError:
        try:
            # If the first attempt fails, try parsing as 24-hour format like 14:30
            user_time = datetime.strptime(usr_time, "%H:%M")
        except ValueError:
            # If both attempts fail, handle the error (invalid input)
            return None
    # Format the time as AM/PM
    formatted_time = user_time.strftime("%H:%M")
    # Define the user's local timezone
    utc_offset_minutes = int(usr_timezone) * 60
    # Create a FixedOffset timezone object
    local_timezone = pytz.FixedOffset(utc_offset_minutes)

    # Get the current date in the user's local timezone
    local_datetime = datetime.now(local_timezone)

    # Parse the user's input time
    user_time = datetime.strptime(usr_time, "%I:%M%p")

    # Combine the user's input time with the current date
    user_datetime = local_datetime.replace(hour=user_time.hour, minute=user_time.minute, second=0, microsecond=0)

    return user_datetime

async def delayed_async_task(seconds, task, send_obj=None, send_str=""):
    await asyncio.sleep(seconds)

    if send_obj is not None:
        await task()
        await send_obj.send(content=send_str)

    else:     
        await task()

        
async def delayed_async_start_task(delay, channel, message_content):
    await asyncio.sleep(delay)
    msg = await channel.send(message_content)


async def delayed_async_delete_msg__task(delay, msg):
    await asyncio.sleep(delay)
    msg = await msg.delete()


def pad_name(name):
    if len(name) < 15:
        padded_member_name = name + ' ' * (15 - len(name))
    else:
        padded_member_name = name[:15]
    return padded_member_name


def prep_hash(raw_string: str) -> str:
    cleaned_string = raw_string.strip().replace(" ", "")
    return cleaned_string


def centered_title(title, space_characters, pad_len):
        max_length = pad_len

        if len(title) > max_length:
            truncated_string = title[:max_length - 3] + "..."
        else:
            truncated_string = title
        total_width = 48
        title_width = len(truncated_string)
        hyphens_width = (total_width - title_width) // 2
        hyphens = space_characters * hyphens_width

        centered_title = f"{hyphens} {truncated_string} {hyphens}"

        return centered_title


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
    team_one: List[str] = field(default_factory=list)
    team_two: List[str] = field(default_factory=list)

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
        print(f"{self.team_one}")
        filtered_list = [name for name in self.team_one if name != username]
        print(f"{filtered_list}")
        self.team_one = filtered_list

    def rm_team_two(self, username):
        print(f"{self.team_two}")
        filtered_list = [name for name in self.team_two if name != username]
        print(f"{filtered_list}")
        self.team_two = filtered_list

    def generate_embed(self):
        if isinstance(self.time, str):
            time = self.time
        else:
            time = self.time.strftime('%H:%M')

        pad_len = 40

        embed = discord.Embed(title=f":star::star::star:{centered_title(self.title, ' ', pad_len)}:star::star::star:",
                              colour=discord.Colour.dark_magenta())

        # Set thumbnial if provided, banner is empty string if we need to set
        file = self.banner

        if not self.banner:
            print('not')
            file = discord.File(get_random_picture(), filename="output.png")
            print(f"file is {file}")
            print(get_random_picture())

            # embed.set_image(url="attachment://output.png")
        else:
            embed.set_image(url=file)
            


        embed.add_field(
            name=f":waning_crescent_moon::waning_crescent_moon: {centered_title(self.game_type,  ' ', pad_len)} :waxing_crescent_moon::waxing_crescent_moon: ", value="", inline=False)
        embed.add_field(
            name=f":alarm_clock: START TIME {self.date} {time} (UTC{self.time_zone}) :alarm_clock:", value=f"")
        embed.add_field(
            name=f":loud_sound: VOICE CHANNEL {self.channel} :loud_sound:", value="", inline=False)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name=f":dog2:~~-----~~Team One~~-----~~:dog2:",
                        value=self.get_roster(self.team_one))
        embed.add_field(name=f":cat2:~~-----~~Team Two~~-----~~:cat2:",
                        value=self.get_roster(self.team_two))
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
        # test_event = create_event(Event)
        # event_id = hash(prep_hash(test_event.user) + prep_hash(test_event.title))
        # self.users_events[event_id] = test_event
        # msg, file = self.users_events[event_id].generate_embed(
        # )
        # message = await self.event_channel.send(embed=msg, file=file)
        # self.users_events[event_id].msg_id = message.id
        # await message.add_reaction("1️⃣")
        # await message.add_reaction("2️⃣")

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
            if payload.emoji.name == '1️⃣':
                self.users_events[event_id].add_team_one(member.display_name)

                embd, _ = self.users_events[event_id].generate_embed()
                await message.edit(embed=embd)
            if payload.emoji.name == '2️⃣':
                self.users_events[event_id].add_team_two(member.display_name)
                embd, _ = self.users_events[event_id].generate_embed()
                await message.edit(embed=embd)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # Get message contents and user

        message = await self.event_channel.fetch_message(payload.message_id)
        member = payload.member

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
        member = discord.utils.get(message.guild.members, id=payload.user_id)
        print(member.display_name)

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
                    event_id = hash(
                        prep_hash(ctx.author.name) + prep_hash(ctx.content))

                    in_progress['event_id'] = event_id
                    self.users_events[event_id] = Event()
                    self.users_events[event_id].user = ctx.author.name
                    self.users_events[event_id].title = ctx.content
                    self.in_progress[ctx.author.name]['position'] += 1
                    position = self.in_progress[ctx.author.name]['position']
                    await ctx.author.send("What game type?")

                case 1:
                    self.users_events[event_id].game_type = ctx.content
                    await ctx.author.send("Date? 'today' to insert todays date")
                    self.in_progress[ctx.author.name]['position'] += 1
                    position = self.in_progress[ctx.author.name]['position']

                case 2:
                    if ctx.content == "today":
                        current_datetime = datetime.now()
                        formatted_date = current_datetime.strftime(
                            "%A, %m/%d/%Y")
                        self.users_events[event_id].date = str(formatted_date)
                        self.in_progress[ctx.author.name]['position'] += 1
                        position = self.in_progress[ctx.author.name]['position']

                    else:
                        self.users_events[event_id].date = ctx.content
                        self.in_progress[ctx.author.name]['position'] += 1
                        position = self.in_progress[ctx.author.name]['position']

                    timezones = "\n".join(
                        f"{abbreviation}: UTC {utc_offset}" for abbreviation, utc_offset in timezone_dict.items())

                    await ctx.author.send(f"Time Zone? You will set your start time after this. Common US timezones:\n{timezones} \n *if you dont see your timezone, input the UTC offset, as a negative or positive numberA*")

                case 3:
                    if timezone_dict.get(ctx.content.upper()):
                        self.users_events[event_id].time_zone = int(timezone_dict[ctx.content.upper()])
                        self.in_progress[ctx.author.name]['position'] += 1
                        position = self.in_progress[ctx.author.name]['position']
                        await ctx.author.send(f"Start Time?: e.g. 4:30PM or 14:30")
                        return
                    try:
                        if str(ctx.content.isnumeric()):
                            user_offset = int(ctx.content)
                            if -12 <= user_offset <= 14:
                                self.in_progress[ctx.author.name]['position'] += 1
                                position = self.in_progress[ctx.author.name]['position']
                                self.users_events[event_id].time_zone = user_offset
                                await ctx.author.send(f"Start Time?: e.g. 4:30PM or 14:30")
                                return

                            else:
                                # Outside the acceptable range
                                await ctx.author.send(f"Please provide a UTC offset within the range of -12 to 14.")
                    except ValueError:
                        # Not a numeric input
                        await ctx.author.send(f"Please provide a numeric UTC offset.")
                
                        
                case 4:
                    self.users_events[event_id].time = convert_user_input_to_utc(ctx.content,
                                                                                 self.users_events[event_id].time_zone)
                    logging.info(self.users_events[event_id].time)
                    self.in_progress[ctx.author.name]['position'] += 1
                    position = self.in_progress[ctx.author.name]['position']
                    await ctx.author.send("Voice Channel link?")


                case 5:
                    self.users_events[event_id].channel = ctx.content
                    self.in_progress[ctx.author.name]['position'] += 1
                    position = self.in_progress[ctx.author.name]['position']
                    await ctx.author.send("Banner? 'pass' for a default banner")

                case 6:
                    try:
                        if len(ctx.attachments) > 0:
                            self.users_events[event_id].banner = ctx.attachments[0].url
                            msg, file = self.users_events[event_id].generate_embed(
                            )
                            message = await self.event_channel.send(embed=msg, file=file)
                        else:
                            msg, file = self.users_events[event_id].generate_embed(
                            )
                            file = discord.File(get_random_picture(), filename="output.png")
                            message = await self.event_channel.send(embed=msg, file=file)
                        self.users_events[event_id].msg_id = message.id
                        await message.add_reaction("1️⃣")
                        await message.add_reaction("2️⃣")
                        await ctx.author.send("Event created.")
                        self.in_progress[ctx.author.name]['position'] += 1
                        position = self.in_progress[ctx.author.name]['position']
                    except Exception as e:
                        await ctx.author.send(f"error {e}")
                        await ctx.author.send("Title of Event??")
                        self.in_progress[ctx.author.name]['position'] = 0


  

                case 7:
                    if self.in_progress.get(ctx.author.name):
                        self.in_progress[(ctx.author.name)] = None

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

    async def events_loop(self):
        reminder_delay = 120
        clean_up_delay = 300

        while True:
            events_to_remove = []

            for evt_id, evt in self.users_events.items():
                if evt.time and evt.time_zone and evt.msg_id:
                    given_datetime = convert_user_time_to_utc(evt.time, evt.time_zone).replace(tzinfo=timezone.utc)
                    current_datetime_in_desired_timezone = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(hours=int(evt.time_zone))
                    if given_datetime + timedelta(seconds=-reminder_delay) < current_datetime_in_desired_timezone:
                        users = evt.team_one + evt.team_two
                        mention_strings = [f"<@{member.id}>" for member in self.event_channel.guild.members if member.name in users]
                        mention_string = ' '.join(mention_strings)
                        reminder = await self.event_channel.send(f"Hey {mention_string}, there's an event happening in {reminder_delay} minutes, {evt.title}, ({evt.game_type}) with {evt.user}")
                        deleyed_reminder_del = delayed_async_task(reminder_delay, reminder.delete)
                        task = asyncio.create_task(deleyed_reminder_del)
                        delayed_start = delayed_async_start_task(reminder_delay, self.event_channel, f"Hey {mention_string}, {evt.title} happening now!")
                        task_two = asyncio.create_task(delayed_start)
                        delete_event = await self.event_channel.fetch_message(evt.msg_id)
                        task_three = delayed_async_delete_msg__task(clean_up_delay + reminder_delay, delete_event)
                        events_to_remove.append(evt_id)
                        await asyncio.gather(task, task_two, task_three)
                        break


            for evt_id in events_to_remove:
                print('to rm')
                del self.users_events[evt_id]

            await asyncio.sleep(1)

async def setup(bot):
    await bot.add_cog(EventCommand(bot))
