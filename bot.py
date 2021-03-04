import os, sys, math, traceback, asyncio
from Utilities import Utilities
from Economy import Economy
from Gambling import Gambling
from Utils import *

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command('help')

bot_prefix = '.'

bot.add_cog(Utilities(bot))
bot.add_cog(Economy(bot))
bot.add_cog(Gambling(bot))


@bot.event
async def on_message(ctx):
	global bot_prefix
	bot_prefix = get_prefix(None, ctx)
	for x in bot.cogs:
		cog = bot.cogs[x]
		cog.prefix = bot_prefix

	if ctx.author.id == bot.user.id:
		return
	
	if bot.user.mentioned_in(ctx):
		await ctx.channel.send(f'My prefix is `{get_prefix(None, ctx)}`')

	await bot.process_commands(ctx)

@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Game(name='.help'))
	print(f'{bot.user.name} is active')

@bot.event
async def on_guild_remove(guild):
	with open('prefix.json', 'r') as f:
		prefixes = json.load(f)

	prefixes.pop(str(guild.id))

	with open('prefix.json', 'w') as f:
		json.dump(prefixes, f, indent = 4)
	
# Unknown command
@bot.event
async def on_command_error(ctx, error):
	# if command has local error handler, return
	if hasattr(ctx.command, 'on_error'):
		return

	# get the original exception
	error = getattr(error, 'original', error)

	if isinstance(error, commands.CommandNotFound):
		await ctx.send('Invalid Command')
		return

	if isinstance(error, commands.BotMissingPermissions):
		missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
		if len(missing) > 2:
			fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
		else:
			fmt = ' and '.join(missing)
		_message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
		await ctx.send(_message)
		return

	if isinstance(error, commands.DisabledCommand):
		await ctx.send('This command has been disabled.')
		return

	if isinstance(error, commands.CommandOnCooldown):
		await ctx.send("This command is on cooldown, please retry in {}s.".format(math.ceil(error.retry_after)))
		return

	if isinstance(error, commands.MissingPermissions):
		missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
		if len(missing) > 2:
			fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
		else:
			fmt = ' and '.join(missing)
		_message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
		await ctx.send(_message)
		return

	if isinstance(error, commands.UserInputError):
		await ctx.send("Invalid Arguments.")
		return

	if isinstance(error, commands.NoPrivateMessage):
		try:
			await ctx.author.send('This command cannot be used in direct messages.')
		except discord.Forbidden:
			pass
		return

	if isinstance(error, commands.CheckFailure):
		await ctx.send("You do not have permission to use this command.")
		return

	# ignore all other exception types, but print them to stderr
	print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)

	traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


bot.run(TOKEN)