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
	with open('milk.json', 'r') as f:
		balances = json.load(f)
	
	balances[user] = 0.0

	with open('milk.json', 'w') as f:
		json.dump(balances, f, indent=4)

def edit_user_milk(user, amount):
	with open('milk.json', 'r') as f:
		balances = json.load(f)
	
	balance = balances[user]
	balance += amount
	balances[user] = balance
	
	with open('milk.json', 'w') as f:
		json.dump(balances, f, indent=4)

async def pre_gambling(ctx, amount_to_bet):
	bet = 0
	try:
		bet = float(amount_to_bet)
	except ValueError:
		await ctx.send('You must specify an amount to bet.')
		return None

	user_balance = 0
	
	try:
		with open('milk.json', 'r') as f:
			balances = json.load(f)
		
		user_balance = balances[ctx.author.name]
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


class Utilities(commands.Cog):
	"""Helpful commands"""
	def __init__(self, bot):
		self.bot = bot
		self.emoji = ':wrench:'

	@commands.command()
	async def help(self, ctx, *cog):
		"""Displays help message // `.help [section]`"""
		try:
			if not cog:
				halp=discord.Embed(title='Section Listing',
								description='Use `.help [section]` to find out more about them!',
								color=discord.Color.blue())
				cogs_desc = ''
				for x in self.bot.cogs:
					cogs_desc += ('{} {} - {}'.format(self.bot.cogs[x].emoji, x,self.bot.cogs[x].__doc__)+'\n')
				halp.add_field(name='Sections',value=cogs_desc[0:len(cogs_desc)-1],inline=False)
				cmds_desc = ''
				
				for y in self.bot.commands:
					if not y.cog_name and not y.hidden:
						cmds_desc += ('{} - {}'.format(y.name,y.help)+'\n')
				if len(cmds_desc) > 0:
					halp.add_field(name='Uncategorized Commands',value=cmds_desc[0:len(cmds_desc)-1],inline=False)
				await ctx.send('',embed=halp)
			else:
				if len(cog) > 1:
					halp = discord.Embed(title='Error!',description='You must specify 1 section',color=discord.Color.red())
					await ctx.send('',embed=halp)
				else:
					found = False
					for x in self.bot.cogs:
						for y in cog:
							if x == y:
								halp=discord.Embed(title=cog[0]+' Command Listing',description=self.bot.cogs[cog[0]].__doc__, color=discord.Color.blue())
								for c in self.bot.get_cog(y).get_commands():
									if not c.hidden:
										halp.add_field(name=c.name,value=c.help,inline=False)
								found = True
					if not found:
						halp = discord.Embed(title='Error!',description=f'{cog[0]} not found!',color=discord.Color.red())
					await ctx.send('',embed=halp)
		except:
			await ctx.send(f'{ctx.guild.owner.mention} An error occurred')
	
	@commands.command(name='prefix')
	@commands.has_permissions(administrator=True)
	async def change_prefix(self, ctx, new_prefix):
		"""Change the Bot's Prefix // `.prefix {new_prefix}`"""
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
		"""Get the bot's ping // `.ping`"""
		await ctx.send(f'{int(self.bot.latency * 1000)}ms')

class Economy(commands.Cog):
	"""Different commands that pertain to the economy"""
	def __init__(self, bot):
		self.bot = bot
		self.emoji = ':moneybag:'
	
	def remove_exclamation_point(self, string):
		new_str = ''
		for char in string:
			if char == '!':
				continue
			new_str += char
		
		return new_str

	@commands.command()
	async def leaderboard(self, ctx):
		"""Check the users with the top 5 milk amounts"""
		with open('milk.json', 'r') as f:
			balances = json.load(f)
		
		new_balances = sorted(balances.items(), key=lambda kv: kv[1], reverse=True)[:5]
		
		desc = ''
		for i in new_balances:
			i = map(str, i)
			desc += ' - '.join(i) + '\n'

		message = discord.Embed(title='Top 5 Milk Owners', description=desc, color=0xffff00)
		await ctx.send('', embed=message)

	@commands.command(name='balance')
	async def check_balance(self, ctx, *account):
		"""Check the amount of milk that you have acquired // `.balance [account_to_check]`"""

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
		
		with open('milk.json', 'r') as f:
			balances = json.load(f)
		
		try:
			bal = discord.Embed(title=f'{account_name}\'s Balance', description=f'{str(balances[account_name])} milk units', color=discord.Color.green())
			await ctx.send('', embed=bal)
		except KeyError:
			balances[account_name] = 0.0

			with open('milk.json', 'w') as f:
				json.dump(balances, f, indent=4)
			
			bal = discord.Embed(title=f'{account_name}\'s Balance', description='0 milk units', color=discord.Color.green())
			await ctx.send('', embed=bal)

class Gambling(commands.Cog):
	"""Commands for gambling your milk"""
	def __init__(self, bot):
		self.bot = bot
		self.emoji = ':game_die:'

	def blackjack_check_aces(self, hand, conversion):
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
		"""Bet your milk on a coinflip // `.coinflip {amount_to_bet} {heads_or_tails}`"""
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
	async def blackjack(self, ctx, amount_to_bet):
		"""Bet your milk to play Blackjack // `.blackjack {amount_to_bet}`"""
		bet = await pre_gambling(ctx, amount_to_bet)
		if bet is None:
			return

		suits = [':clubs:', ':spades:', ':hearts:', ':diamonds:']
		numbers = ['A', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
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
		dealer_str_initial = f'{dealer_suits[0]}{dealer_nums[0]}\t<:card:797302274535063582>'
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