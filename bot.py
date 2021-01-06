import os, json, random

import discord, nacl
from discord.ext import commands
from discord.voice_client import VoiceClient
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

def get_prefix(client, message):
	with open('prefix.json', 'r') as f:
		prefixes = json.load(f)

	try:
		return prefixes[str(message.guild.id)]
	except KeyError:
		return '.'

bot = commands.Bot(command_prefix=get_prefix)

@bot.command(name = 'prefix', help = 'Change the bot\'s prefix, must have a role named "prefix" to use')
@commands.has_role('prefix')
async def change_prefix(ctx, new_prefix):
	# Check validity
	if len(new_prefix) == 1 and not new_prefix.isalpha():
		with open('prefix.json', 'r') as f:
			prefixes = json.load(f)

		prefixes[str(ctx.guild.id)] = new_prefix

		with open('prefix.json', 'w') as f:
			json.dump(prefixes, f, indent = 4)

		await ctx.send(f'Prefix changed to {new_prefix}')
	elif new_prefix.isalpha():
		await ctx.send('Prefix can\'t be a letter')
	else:
		await ctx.send('Prefix too long')

@bot.command(name='balance', help='Check the amount of milk that you have acquired.')
async def check_balance(ctx, *account):
	account_to_check = ''
	try:
		account_to_check = account[0]
	except IndexError:
		account_to_check = ctx.author.mention
	
	with open('milk.json', 'r') as f:
		balances = json.load(f)
	
	try:
		await ctx.send(balances[account_to_check])
	except KeyError:
		balances[account_to_check] = 0

		with open('milk.json', 'w') as f:
			json.dump(balances, f, indent=4)
		
		await ctx.send(0)


@bot.event
async def on_message(ctx):
	if ctx.author.id == bot.user.id:
		return

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
	if isinstance(error, commands.CommandNotFound):
		await ctx.send('Invalid Command')

bot.run(TOKEN)