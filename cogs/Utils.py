import discord, json, time, random, asyncio
from discord.ext import commands

def get_prefix(client, message):
	with open('prefix.json', 'r') as f:
		prefixes = json.load(f)

	try:
		if message.channel.type != discord.ChannelType.private:
			return prefixes[str(message.guild.id)]
		else:
			return '.'
	except KeyError:
		return '.'

def add_user_to_milk(user: str):
	with open('user.json', 'r') as f:
		users = json.load(f)

	if user in users:
		users[user] = {"balance": 0.0, "daily": 0.0, "work_cd": 0.0, "job": "unemployed", "cdstate": "active"}
	else:
		users[user] = {"balance": 0.0, "daily": 0.0, "work_cd": 0.0, "job": "unemployed", "cdstate": "active"}

	with open('user.json', 'w') as f:
		json.dump(users, f, indent=4)

def edit_user_milk(user: str, amount: float):
	with open('user.json', 'r') as f:
		users = json.load(f)
	
	balance = users[user]["balance"]
	balance += amount
	users[user]["balance"] = balance
	
	with open('user.json', 'w') as f:
		json.dump(users, f, indent=4)

async def pre_gambling(ctx, amount_to_bet: float):
	bet = 0
	try:
		bet = float(amount_to_bet)
	except ValueError:
		await ctx.send('You must specify an amount to bet.')
		return None

	user_balance = 0
	
	try:
		with open('user.json', 'r') as f:
			users = json.load(f)
		
		user_balance = users[ctx.author.name]['balance']
		if bet > user_balance:
			await ctx.send('You cannot bet more than your balance')
			return None

	except KeyError:
		add_user_to_milk(ctx.author.name)

		await ctx.send('You cannot bet with no milk')
		return None
	
	return bet

async def is_on_cooldown(ctx, length: float, purpose: str):
	with open('user.json', 'r') as f:
		users = json.load(f)

	if ctx.author.name not in users:
		add_user_to_milk(ctx.author.name)
		with open('user.json', 'r') as f:
			users = json.load(f)
	
	if users[ctx.author.name]['cdstate'] == 'off':
		return False

	old_time = users[ctx.author.name][purpose]

	difference = time.time() - old_time

	if difference >= length:
		users[ctx.author.name][purpose] = time.time()
		
		with open('user.json', 'w') as f:
			json.dump(users, f, indent=4)

		return False

	else:
		string = ''
		time_left = length - difference

		if time_left >= 86400:
			days = time_left // 86400
			hours = (time_left % 86400) // 3600
			minutes = (time_left % 3600) // 60
			string += str(int(days)) + ' days ' + str(int(hours)) + ' hr ' + str(int(minutes)) + ' min '

		elif time_left >= 3600:
			hours = time_left // 3600
			minutes = (time_left % 3600) // 60
			string += str(int(hours)) + ' hr ' + str(int(minutes)) + ' min '
		elif time_left >= 60:
			minutes = (time_left % 3600) // 60
			string += str(int(minutes)) + ' min '
		
		seconds = (time_left % 3600) % 60
		string += str(int(seconds)) + ' sec'

		embed = discord.Embed(title='You cannot use this command yet!',
								description=f'Please wait {string} to use this command.',
								color=discord.Color.red())

		await ctx.send('', embed=embed)
		return True

def int_to_str(num):
	if num >= 1000:
		num_of_commas = (len(str(num)) - 1) // 3
		comma_idx = len(str(num)) % 3
		new_num = list(str(num))
		if comma_idx != 0:
			new_num.insert(comma_idx, ',')
			transformation = 1
			factor = 4
		else:
			transformation = 0
			factor = 3

		for i in range(num_of_commas - transformation):
			new_num.insert(comma_idx + factor * (i + 1), ',')

		return ''.join(new_num)

	else:
		return str(num)