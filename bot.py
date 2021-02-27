import os, json, random, time, sys, math, traceback, asyncio

import discord
from discord.ext import commands
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

def add_user_to_milk(user):
	with open('user.json', 'r') as f:
		users = json.load(f)

	if user in users:
		users[user]["balance"] = 0.0
	else:
		users[user] = {"balance": 0.0, "daily": 0.0, "work_cd": 0.0, "job": "unemployed"}

	with open('user.json', 'w') as f:
		json.dump(users, f, indent=4)

def edit_user_milk(user, amount):
	with open('user.json', 'r') as f:
		users = json.load(f)
	
	balance = users[user]["balance"]
	balance += amount
	users[user]["balance"] = balance
	
	with open('user.json', 'w') as f:
		json.dump(users, f, indent=4)

async def pre_gambling(ctx, amount_to_bet):
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

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command('help')


class Job:
	def __init__(self, name, salary):
		self.name = name
		self.salary = salary


class Utilities(commands.Cog):
	"""Helpful commands"""
	def __init__(self, bot):
		self.bot = bot
		self.emoji = ':wrench:'

	@commands.command()
	async def help(self, ctx, *command):
		"""Description:
		Displays help message
		
		Use:
		`.help [command]`"""
		if not command:
			halp=discord.Embed(title='Command Listing',
							description='Use `.help [command]` to find out more about them!',
							color=discord.Color.blue())
			for x in self.bot.cogs:
				cog = self.bot.cogs[x]
				cmds_str = ''
				for cmd in cog.get_commands():
					cmds_str += f'`.{cmd}` '
				halp.add_field(name=cog.emoji + x, value=cmds_str, inline=False)

			cmds_desc = ''
			for y in self.bot.commands:
				if not y.cog_name and not y.hidden:
					cmds_desc += ('{} - {}'.format(y.name.title(), y.help)+'\n')
			if len(cmds_desc) > 0:
				halp.add_field(name='Uncategorized Commands',value=cmds_desc[0:len(cmds_desc)-1],inline=False)
			await ctx.send('',embed=halp)
		else:
			if len(command) > 1:
				halp = discord.Embed(title='Error!',description='You must specify a single command.',color=discord.Color.red())
				await ctx.send('',embed=halp)
			else:
				found = False
				for x in self.bot.cogs:
					cog = self.bot.cogs[x]
					for y in cog.walk_commands():
						if command[0].lower() == y.name:
							halp = discord.Embed(title='gg')
							halp = discord.Embed(title=y.name.title() + ' Description', description=y.help, color=discord.Color.blue())

							found = True
				if not found:
					halp = discord.Embed(title='Error!', description=f'{command[0]} not found!', color=discord.Color.red())
				await ctx.send('',embed=halp)
	
	@commands.command(name='prefix')
	@commands.has_permissions(administrator=True)
	async def change_prefix(self, ctx, new_prefix):
		"""Description:
		Change the Bot's Prefix
		
		Use:
		`.prefix {new_prefix}`"""
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

	@commands.command(name='ping')
	async def get_ping(self, ctx):
		"""Description:
		Get the bot's ping
		
		Use:
		`.ping`"""
		ping = ctx.message
		pong = await ctx.send('Ping is')
		delta = pong.created_at - ping.created_at
		delta = int(delta.total_seconds() * 1000)
		await pong.edit(content=f'Ping is {delta}ms\nLatency is {str(self.bot.latency * 1000)[:2]}ms')

class Economy(commands.Cog):
	"""Different commands that pertain to the economy"""

	working_gaming = False
	working_mistake = False
	working_cangaroo = False

	canga_row = 0
	canga_column = 0

	def __init__(self, bot):
		self.bot = bot
		self.emoji = ':moneybag:'
		self.job_list = [Job('Simmons Gaming Industries', 250), Job('Midstake', 500), Job('Cangaroo Containment Facility', 1000)]
		self.job_aliases = ['SMI', 'M', 'CCF']
		self.job_names = [job.name for job in self.job_list]

	@staticmethod
	def get_working_bools():
		return (Economy.working_gaming, Economy.working_mistake, Economy.working_cangaroo)

	@staticmethod
	def remove_exclamation_point(string):
		new_str = ''
		for char in string:
			if char == '!':
				continue
			new_str += char
		
		return new_str

	@classmethod
	async def gaming(self, ctx):
		pass

	@classmethod
	async def mistake(self, ctx):
		pass

	@classmethod
	async def cangaroo(self, message):
		if message.content == str(Economy.canga_row) + ' ' + str(Economy.canga_column):
			embed = discord.Embed(title='Good job! You caught the Cangaroo before it could escape. You have received 1000mu', color=discord.Color.green())
			edit_user_milk(message.author.name, 1000)
		else:
			embed = discord.Embed(title='Too bad! You couldn\'t catch the Cangaroo before it escaped. Try again next time.')

		await message.channel.send('', embed=embed)

		Economy.working_cangaroo = False

	@commands.command()
	async def leaderboard(self, ctx):
		"""Description:
		Check the users with the top 5 milk amounts
		
		Use:
		`.leaderboard`"""
		with open('user.json', 'r') as f:
			users = json.load(f)
		
		balance_list = {}
		for user, val in users.items():
			balance_list[user] = val['balance']
		
		new_balances = sorted(balance_list.items(), key=lambda kv: kv[1], reverse=True)[:5]
		
		desc = ''
		for i in new_balances:
			i = map(str, i)
			desc += ' - '.join(i) + '\n'

		message = discord.Embed(title='Top 5 Milk Owners', description=desc, color=0xffff00)
		await ctx.send('', embed=message)

	@commands.command(name='balance')
	async def check_balance(self, ctx, *account):
		"""Description:
		Check the amount of milk that you have acquired
		
		Use:
		`.balance [account_to_check]`"""

		account_member = None
		if account:
			account_id = int(account[0][3:-1]) if '!' in account[0] else int(account[0][2:-1])
			account_member = ctx.guild.get_member(account_id)
			if account_member is None:
				await ctx.send('User not found')
				return
		else:
			account_member = ctx.author
		
		account_name = account_member.name
		
		with open('user.json', 'r') as f:
			users = json.load(f)
		
		try:
			bal = discord.Embed(title=f'{account_name}\'s Balance', description=f'{str(users[account_name]["balance"])} milk units', color=discord.Color.green())
			await ctx.send('', embed=bal)
		except KeyError:
			add_user_to_milk(account_name)

			with open('milk.json', 'w') as f:
				json.dump(users, f, indent=4)
			
			bal = discord.Embed(title=f'{account_name}\'s Balance', description='0 milk units', color=discord.Color.green())
			await ctx.send('', embed=bal)

	@commands.command(name='daily')
	async def daily_claim(self, ctx):
		"""Description:
		Claim a 1000 milk unit reward every day!
		
		Use:
		`.daily`"""
		with open('user.json', 'r') as f:
			users = json.load(f)
		
		try:
			old_time = users[ctx.author.name]['daily']

			difference = time.time() - old_time

			if difference >= 86400:
				edit_user_milk(ctx.author.name, 1000)
				embed = discord.Embed(title='You have received 1000 milk units!',
									  description='Come back in 24 hours for another reward.',
									  color=discord.Color.purple())

				with open('user.json', 'r') as f:
					refreshed_users = json.load(f)
				
				refreshed_users[ctx.author.name]['daily'] = time.time()

				with open('user.json', 'w') as f:
					json.dump(refreshed_users, f, indent=4)

			else:
				string = ''
				time_left = 86400 - difference

				if time_left >= 3600:
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
		
		except KeyError:
			add_user_to_milk(ctx.author.name)
			edit_user_milk(ctx.author.name, 1000)
			embed = discord.Embed(title='You have received 1000 milk units!',
									description='Come back in 24 hours for another reward.',
									color=discord.Color.purple())

			with open('user.json', 'r') as f:
				refreshed_users = json.load(f)
			
			refreshed_users[ctx.author.name]['daily'] = time.time()

			with open('user.json', 'w') as f:
				json.dump(refreshed_users, f, indent=4)
		
		await ctx.send('', embed=embed)

	@commands.command()
	async def work(self, ctx, *args):
		"""Description:
		Work at your job or choose a new job.
		
		Use:
		`.work [job | list]`"""

		with open('user.json', 'r') as f:
			users = json.load(f)

		if ctx.author.name not in users:
			add_user_to_milk(ctx.author.name)
		
		if args:
			if args[0] == 'list':
				jobs = '\n\n'.join([job.name + ' - ' + str(job.salary) + f'mu\n({self.job_aliases[self.job_list.index(job)]})' for job in self.job_list])

				embed = discord.Embed(title='Use `.work [job]` to choose a job.', description=jobs, color=discord.Color.green())
				await ctx.send('', embed=embed)
				return
			
			job = ' '.join(args)

			if job in self.job_names or job in self.job_aliases:
				if job in self.job_aliases:
					job = self.job_names[self.job_aliases.index(job)]

				users[ctx.author.name]['job'] = job
				with open('user.json', 'w') as f:
					json.dump(users, f, indent=4)

				embed = discord.Embed(title=f'You are now working at {job}!', color=discord.Color.green())
				await ctx.send('', embed=embed)

			else:
				embed = discord.Embed(title='This job does not exist.', color=discord.Color.red())
				await ctx.send('', embed=embed)
		
		else:
			last_work_time = users[ctx.author.name]['work_cd']
			difference = time.time() - last_work_time

			if difference >= 3600:
				users[ctx.author.name]['work_cd'] = time.time()

				with open('user.json', 'w') as f:
					json.dump(users, f, indent=4)

				job = users[ctx.author.name]['job']
				
				if job == 'Simmons Gaming Industries':
					await self.gaming(ctx)

				elif job == 'Midstake':
					await self.mistake(ctx)

				elif job == 'Cangaroo Containment Facility':
					emojis = [':llama:', ':dromedary_camel:', ':giraffe:', ':racehorse:', ':dog2:', ':ox:']
					grid = [[], [], [], [], []]
					grid_index = 0

					for i in range(25):
						if i % 5 == 0 and i != 0:
							grid_index += 1
						
						grid[grid_index].append(random.choice(emojis))

					canga_row = random.randint(0, 4)
					canga_column = random.randint(0, 4)

					grid[canga_column][canga_row] = ':kangaroo:'
					Economy.canga_row, Economy.canga_column = canga_row + 1, canga_column + 1

					grid_str = ''

					for i in range(5):
						for j in range(5):
							grid_str += grid[i][j]
						grid_str += '\n'

					grid_embed = discord.Embed(title='The Cangaroo has escaped! Memorize the Cangaroo\'s location.', description=grid_str, color=discord.Color.purple())
					grid_msg = await ctx.send('', embed=grid_embed)

					await asyncio.sleep(5)

					await grid_msg.delete()
					instructions_embed = discord.Embed(title='Type which row and column the Cangaroo was last spotted separated by spaces.', color=discord.Color.purple())
					await ctx.send('', embed=instructions_embed)

					Economy.working_cangaroo = True
				
			else:
				cd_str = ''
				time_left = 3600 - difference

				if time_left > 60:
					minutes = int(time_left // 60)
					cd_str += str(minutes) + 'min '
				
				seconds = int(time_left % 60)
				cd_str += str(seconds) + 'sec'

				embed = discord.Embed(title='This command is on cooldown.', description=f'You can work again in {cd_str}.')
				await ctx.send('', embed=embed)

class Gambling(commands.Cog):
	"""Commands for gambling your milk"""
	def __init__(self, bot):
		self.bot = bot
		self.emoji = ':game_die:'

	@staticmethod
	def blackjack_check_aces(hand, conversion):
		num_of_aces = 0

		for i in hand:
			if i == 'A':
				num_of_aces += 1

		numsum = 0

		for card in hand:
				if card != 'A':
					numsum += conversion[card]

		for i in range(num_of_aces):
			if numsum + 11 > 21:
				numsum += 1
			else:
				numsum += 11
		
		return numsum

	@commands.command(name='coinflip')
	async def coin_flip(self, ctx, amount_to_bet, heads_or_tails):
		"""Description:
		Bet your milk on a coinflip
		
		Use:
		`.coinflip {amount_to_bet} {heads_or_tails}`"""
		bet = await pre_gambling(ctx, amount_to_bet)
		if bet is None:
			return
		
		flipping = discord.Embed(title=':coin: Flipping Coin...', color=0xffff00)
		flipping_msg = await ctx.send('', embed=flipping)
		await asyncio.sleep(1.5)

		choice = heads_or_tails.lower()
		if choice != 'heads' and choice != 'tails':
			await ctx.send('You must specify to bet on either heads or tails')
			return
		
		choices = ['heads', 'tails']
		result = random.choice(choices)
		if choice == result:
			edit_user_milk(ctx.author.name, bet)
			message = discord.Embed(title=f'It was {result}! You Won!',
									description=f'You won {bet} milk units!',
									color=discord.Color.green())
			await flipping_msg.edit(embed=message)
		else:
			edit_user_milk(ctx.author.name, -bet)
			message = discord.Embed(title=f'It was {result}. You lost...',
									description=f'You lost {bet} milk units.',
									color=discord.Color.red())
			await flipping_msg.edit(embed=message)

	@commands.command()
	@commands.cooldown(5, 3)
	async def blackjack(self, ctx, amount_to_bet):
		"""Description:
		   Bet your milk to play Blackjack

		   Use:
		   `.blackjack {amount_to_bet}`"""
		bet = await pre_gambling(ctx, amount_to_bet)
		if bet is None:
			return

		suits = [':clubs:', ':spades:', ':hearts:', ':diamonds:']
		numbers = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
		conversion = {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 'J': 10, 'Q': 10, 'K': 10}

		player_nums = [random.choice(numbers), random.choice(numbers)]
		player_suits = [random.choice(suits), random.choice(suits)]
		player_str_initial = f'{player_suits[0]}{player_nums[0]}\t{player_suits[1]}{player_nums[1]}'
		
		if 'A' in player_nums:
			player_sum = self.blackjack_check_aces(player_nums, conversion)
		else:
			player_sum = conversion[player_nums[0]] + conversion[player_nums[1]]

		dealer_nums = [random.choice(numbers)]
		dealer_suits = [random.choice(suits)]
		dealer_str_initial = f'{dealer_suits[0]}{dealer_nums[0]}\t<:card:798689937436180490>'
		if 'A' in dealer_nums:
			dealer_sum = self.blackjack_check_aces(dealer_nums, conversion)
		else:
			dealer_sum = conversion[dealer_nums[0]]

		message1 = discord.Embed(title=f'Dealer\'s Hand ({dealer_sum})', description=dealer_str_initial)
		message1.add_field(name=f'Your Hand ({player_sum})', value=player_str_initial)

		initial_hands = await ctx.send('', embed=message1)
		await initial_hands.add_reaction('✊')
		await initial_hands.add_reaction('✋')

		def check(reaction, user):
			return user == ctx.author and str(reaction.emoji) in ['✊', '✋']
		
		try:
			reaction, _ = await self.bot.wait_for('reaction_add', timeout=10, check=check)

			while reaction.emoji == '✊':
				player_nums.append(random.choice(numbers))
				player_suits.append(random.choice(suits))
				if 'A' in player_nums:
					player_sum = self.blackjack_check_aces(player_nums, conversion)
				else:
					player_sum += conversion[player_nums[-1]]

				player_str_next = player_str_initial + f'\t{player_suits[-1]}{player_nums[-1]}'
				
				message1.set_field_at(0, name=f'Your Hand ({player_sum})', value=player_str_next)

				if player_sum > 21:
					message1.add_field(name='Busted!', value=f'You lost {bet} milk units.', inline=False)
					message1.color = discord.Color.red()
					edit_user_milk(ctx.author.name, -bet)
					await initial_hands.edit(embed=message1)
					return
				
				await initial_hands.edit(embed=message1)
				await initial_hands.clear_reactions()
				await initial_hands.add_reaction('✊')
				await initial_hands.add_reaction('✋')

				reaction, _ = await self.bot.wait_for('reaction_add', timeout=10, check=check)


			dealer_nums.append(random.choice(numbers))
			dealer_suits.append(random.choice(suits))
			dealer_str = f'{dealer_suits[0]}{dealer_nums[0]}\t{dealer_suits[1]}{dealer_nums[1]}'
			if 'A' in dealer_nums:
				dealer_sum = self.blackjack_check_aces(dealer_nums, conversion)
			else:
				dealer_sum += conversion[dealer_nums[1]]
			message1.title = f'Dealer\'s Hand ({dealer_sum})'
			message1.description = dealer_str
			await initial_hands.edit(embed=message1)

			while dealer_sum <= 16:
				await asyncio.sleep(1.5)

				dealer_nums.append(random.choice(numbers))
				dealer_suits.append(random.choice(suits))
				if 'A' in dealer_nums:
					dealer_sum = self.blackjack_check_aces(dealer_nums, conversion)
				else:
					dealer_sum += conversion[dealer_nums[-1]]
				message1.title = f'Dealer\'s Hand ({dealer_sum})'
				dealer_str += f'\t{dealer_suits[-1]}{dealer_nums[-1]}'
				message1.description = dealer_str

				await initial_hands.edit(embed=message1)

			if dealer_sum > 21 or player_sum > dealer_sum:
				message1.add_field(name='You won!', value=f'You won {bet} milk units.', inline=False)
				message1.color = discord.Color.green()
				edit_user_milk(ctx.author.name, bet)
				await initial_hands.edit(embed=message1)
				return
			
			elif player_sum < dealer_sum:
				message1.add_field(name='You lost.', value=f'You lost {bet} milk units', inline=False)
				message1.color = discord.Color.red()
				edit_user_milk(ctx.author.name, -bet)
				await initial_hands.edit(embed=message1)
				return

			elif player_sum == dealer_sum:
				message1.add_field(name='Push!', value='It was a tie.', inline = False)
				await initial_hands.edit(embed=message1)
				return

		except asyncio.TimeoutError:
			timeout = discord.Embed(title='Timed Out')
			await initial_hands.edit(embed=timeout)
			await initial_hands.clear_reactions()


bot.add_cog(Utilities(bot))
bot.add_cog(Economy(bot))
bot.add_cog(Gambling(bot))


@bot.event
async def on_message(ctx):
	if ctx.author.id == bot.user.id:
		return
	
	if bot.user.mentioned_in(ctx):
		await ctx.channel.send(f'My prefix is `{get_prefix(None, ctx)}`')

	if Economy.get_working_bools()[2] == True:
		await Economy.cangaroo(ctx)

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