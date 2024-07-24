# snippet.py

import discord
from discord.ext import commands
from pymongo import MongoClient
import certifi

# Connect to MongoDB using MongoClient and the provided connection string
cluster = MongoClient("mongodb+srv://<username>:<password>@<cluster-url>/soar1?retryWrites=true&w=majority", tlsCAFile=certifi.where())

# Select the database and collection
db = cluster["soar1"]
users = db["users"]

# Configure the bot's intents
intents = discord.Intents.default()
intents.members = True

# Initialize the bot with the configured intents
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    """
    Event handler that is called when the bot is ready.
    """
    print("bot is online")

@bot.event
async def on_raw_reaction_add(payload):
    """
    Event handler that is called when a reaction is added to a message.
    Adds a role to a user when they react with a specific emoji.
    """
    message_id = 123456789012345678  # Replace with your message ID
    guild_id = payload.guild_id
    guild = bot.get_guild(guild_id)
    
    if message_id == payload.message_id:
        if payload.emoji.name == '👋':  # Replace with the desired emoji
            role = discord.utils.get(guild.roles, name='user')  # Replace with your role name
            await payload.member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    """
    Event handler that is called when a reaction is removed from a message.
    Removes a role from a user when they remove a specific reaction.
    """
    message_id = 123456789012345678  # Replace with your message ID
    guild_id = payload.guild_id
    guild = bot.get_guild(guild_id)
    
    if message_id == payload.message_id:
        member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
        if payload.emoji.name == '👋':  # Replace with the desired emoji
            role = discord.utils.get(guild.roles, name='user')  # Replace with your role name
            await member.remove_roles(role)

@bot.event
async def on_member_join(member):
    """
    Event handler that is called when a new member joins the guild.
    Creates a user profile in the database for the new member.
    """
    res = users.find_one({"_id": member.id})
    if res is None:
        users.insert_one({
            "_id": member.id, 
            "Name": str(member), 
            "Balance": 0, 
            "UI": 0, 
            "UX": 0, 
            "FE": 0, 
            "BE": 0, 
            "A": 0, 
            "Contracts Completed": 0
        })

@bot.command()
@commands.has_role("admin")
async def assign(ctx, user: discord.Member, role: discord.Role):
    """
    Command that allows an admin to assign a role to a user.
    """
    if role in ctx.guild.roles:
        await user.add_roles(role)

@bot.command()
@commands.has_role("admin")
async def unassign(ctx, user: discord.Member, role: discord.Role):
    """
    Command that allows an admin to remove a role from a user.
    """
    if role in ctx.guild.roles:
        await user.remove_roles(role)

@bot.command()
async def viewprofile(ctx, member: discord.Member = None):
    """
    Command that allows a user to view a member's profile.
    If no member is specified, the profile of the command issuer is shown.
    """
    if member is None:
        member = ctx.author
    
    res = users.find_one({"_id": member.id})
    embed = discord.Embed(
        title=str(member) + "'s User Profile",
        description="This user's skill levels and statistics are shown below." +
                    "\nBalance: " + str(res["Balance"]) +
                    "\nUser Interface: " + str(res["UI"]) +
                    "\nUser Experience: " + str(res["UX"]) +
                    "\nFront End: " + str(res["FE"]) +
                    "\nBack End: " + str(res["BE"]) +
                    "\nAlgorithm: " + str(res["A"]) +
                    "\nContracts Completed: " + str(res["Contracts Completed"]),
        color=discord.Color.dark_blue()
    )
    await ctx.send(embed=embed)

# Run the bot with the specified token
bot.run('<your-bot-token>')
