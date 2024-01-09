

from typing import Optional
import discord
from discord.ext import commands


class Menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles = ""

    @commands.command()
    async def roleinactivity(ctx, role : discord.Role): 
        print(role.members)

    @commands.Cog.listener()
    async def on_ready(self, ctx, role: discord.Role):
        self.roles = "\n".join(str(member) for member in role.members)
        print(self.roles)
        async for member in guild.fetch_members():
                member = await guild.fetch_member(member.id) # <== Fetches member object
                member_id = member.id  # Integer
                displayName = member.display_name  # String
                discriminator = member.discriminator  # String
                mention = member.mention  # String
                server = guild.name  # String
                # update existing
                User = Member
                _roles = []
                for role in member.roles:  # <== Iterates through each roll and adds them to a list
                    _roles.append(role.name) # adds to list
        
    @commands.command()
    async def menu(self, ctx):
        await ctx.send("Menus!", view=SelectView())

    @commands.command()
    async def roles(self, ctx):
        print(", ".join([str(r.id) for r in ctx.guild.roles]))

    @commands.command(name='names')
    async def names(self, ctx, role_name):
        # Get the role object
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if not role:
            await ctx.send(f"Role {role_name} not found.")
            return

        # Get all members with the specified role
        members = role.members

        # Extract the names of the members
        member_names = [member.name for member in members]

        await ctx.send(f"Members in the role {role_name}: {', '.join(member_names)}")


class Select(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="Option 1",emoji="👌",description="This is option 1!"),
            discord.SelectOption(label="Option 2",emoji="✨",description="This is option 2!"),
            discord.SelectOption(label="Option 3",emoji="🎭",description="This is option 3!")
            ]
        super().__init__(placeholder="Select an option",max_values=3,min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Option 1":
            await interaction.response.edit_message(content="This is the first option from the entire list!")
        elif self.values[0] == "Option 2":
            await interaction.response.send_message("This is the second option from the list entire wooo!",ephemeral=False)
        elif self.values[0] == "Option 3":
            await interaction.response.send_message("Third One!",ephemeral=True)

class SelectView(discord.ui.View):
    def __init__(self, *, timeout = 180):
        super().__init__(timeout=timeout)
        self.add_item(Select())



async def setup(bot):
    await bot.add_cog(Menu(bot))





















# class Select(discord.ui.View):
#     def __init__(self, *, timeout: float | None = 180):
#         super().__init__(timeout=timeout)


# class DropdownView(discord.ui.View):
#     def __init__(self):

#         super().__init__()

#         # Adds the dropdown to our view object.
#         self.add_item(Select())

    
    # @commands.command(name="shit") 
    # async def colour(self, ctx):
    #     """Sends a message with our dropdown containing colours"""

    #     # Create the view containing our dropdown
    #     view = DropdownView()

    #     # Sending a message containing our view
    #     await ctx.send('Pick your favourite colour:', view=view)
