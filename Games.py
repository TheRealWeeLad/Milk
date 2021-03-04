from Utils import *
from discord.ext import commands

class Games(commands.Cog):
    """Commands that allow you to play different games"""

    def __init__(self, bot):
        self.bot = bot