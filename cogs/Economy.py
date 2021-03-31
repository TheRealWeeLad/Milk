import discord, json
from discord.ext import commands
from Utils import (random, asyncio, add_user_to_milk, edit_user_milk, is_on_cooldown, int_to_str)
from itemfuncs import functions

class Item:
	def __init__(self, name: str, description: str, detailed_description: str, emoji: str, cost: int, function):
		self.name = name
		self.description = description
		self.detailed_description = detailed_description
		self.emoji = emoji
		self.cost = cost
		self.use = function
	
	def __str__(self):
		return self.name
	
	def __int__(self):
		return self.cost

class Job:
	def __init__(self, name, salary):
		self.name = name
		self.salary = salary

class Economy(commands.Cog):
	"""Different commands that pertain to the economy"""

	prefix = '.'

	def __init__(self, bot):
		self.bot = bot
		self.emoji = ':moneybag:'
		self.job_list = [Job('Simmons Gaming Industries', 500), Job('Kangaroo Containment Facility', 1000)]
		self.job_aliases = ['SGI', 'KCF']
		self.job_aliases_lower = ['sgi', 'kcf']
		self.job_names = [job.name for job in self.job_list]
		self.job_names_lower = [job.name.lower() for job in self.job_list]
		self.keyboard = ['!', '#', '*', '?']
		self.keyboard.extend(letter for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
		self.keyboard_emojis = [':exclamation:', ':hash:', ':asterisk:', ':question:']
		self.keyboard_emojis.extend([f':regional_indicator_{letter}:' for letter in 'abcdefghijklmnopqrstuvwxyz'])

		cookie = Item('Cookie', 'Does nothing', 'Does literally nothing', ':cookie:', 5, lambda: None)
		milk = Item('Milk Carton', 'Negates command cooldowns', 'Drinking this will allow you to use commands as much as you like without provoking a cooldown.', '<:carton:826231831757717516>', 999999, functions[0])
		self.items = [milk, cookie]
		self.item_strs = list(map(str, self.items))

	@staticmethod
	def remove_exclamation_point(string):
		new_str = ''
		for char in string:
			if char != '!':
				new_str += char
		
		return new_str

	async def gaming(self, ctx):
		keys_length = random.randint(3, 7)
		idxs = [random.randint(0, 29) for i in range(keys_length)]
		key_emojis = ' '.join([self.keyboard_emojis[idxs[i]] for i in range(keys_length)])
		key_chars = ' '.join([self.keyboard[idxs[i]] for i in range(keys_length)])

		instructions_embed = discord.Embed(title='XX_N00B_K1LL3R_69420_XX is about to 360 No Scope you!', 
										   color=discord.Color.blurple())
		instructions_embed.add_field(name='Type the following sequence of keys to dodge his snipe.', value=key_emojis)
		await ctx.send('', embed=instructions_embed)

		def check(msg):
			return msg.author == ctx.author and msg.content.upper() in [key_chars, ''.join(key_chars.split())]

		try:
			await self.bot.wait_for('message', check=check, timeout=10)
		
		except asyncio.TimeoutError:
			embed = discord.Embed(title='You were too slow!', description='You died to XX_N00B_K1LL3R_69420_XX\'s no scope. Unfortunate.', color=discord.Color.red())
			await ctx.send('', embed=embed)
			return
		
		edit_user_milk(ctx.author.name, self.job_list[0].salary)

		win_embed = discord.Embed(title='You correctly input the keys! gj', description=f'XX_N00B_K1LL3R_69420_XX stood no chance against your unparalleled dodging skills. You gained {self.job_list[0].salary}mu.', color=discord.Color.green())
		await ctx.send('', embed=win_embed)

	async def kangaroo(self, ctx):
		emojis = [':llama:', ':dromedary_camel:', ':giraffe:', ':racehorse:', ':dog2:', ':ox:']
		grid = [[], [], [], [], []]
		grid_index = 0

		for i in range(25):
			if i % 5 == 0 and i != 0:
				grid_index += 1
			
			grid[grid_index].append(random.choice(emojis))

		canga_row = random.randint(1, 5)
		canga_column = random.randint(1, 5)

		grid[canga_column - 1][canga_row - 1] = ':kangaroo:'

		grid_str = ''

		for i in range(5):
			for j in range(5):
				grid_str += grid[i][j]
			grid_str += '\n'

		grid_embed = discord.Embed(title='The Kangaroo has escaped! Memorize the Kangaroo\'s location.', description=grid_str, color=discord.Color.purple())
		grid_msg = await ctx.send('', embed=grid_embed)

		await asyncio.sleep(5)

		await grid_msg.delete()
		instructions_embed = discord.Embed(title='Type which row and column the Kangaroo was last spotted separated by spaces.', color=discord.Color.purple())
		instructions_msg = await ctx.send('', embed=instructions_embed)

		def check(message):
			return message.author == ctx.author

		try:
			msg = await self.bot.wait_for('message', check=check, timeout=3)
		
		except asyncio.TimeoutError:
			embed = discord.Embed(title='Too late!', description='The Kangaroo escaped before you could catch it. Try again next time.', color=discord.Color.red())
			await instructions_msg.edit(embed=embed)

		else:
			if msg.content == str(canga_row) + ' ' + str(canga_column):
				embed = discord.Embed(title=f'Good job! You caught the Kangaroo before it could escape. You have received {self.job_list[1].salary}mu.', color=discord.Color.green())
				edit_user_milk(msg.author.name, self.job_list[1].salary)
			else:
				embed = discord.Embed(title='Too bad! You couldn\'t catch the Kangaroo before it escaped. Try again next time.', color=discord.Color.red())

			await ctx.send('', embed=embed)

	@commands.command()
	async def leaderboard(self, ctx):
		"""Description:
		Check the users with the top 5 milk amounts
		
		Use:
		`%sleaderboard`"""
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

		message = discord.Embed(title='Top 5 Milk Owners', description=desc, color=discord.Color.yellow())
		await ctx.send('', embed=message)

	@commands.command(name='balance')
	async def check_balance(self, ctx, *account):
		"""Description:
		Check the amount of milk that you have acquired
		
		Use:
		`%sbalance [account_to_check]`"""

		account_member = None
		if account:
			account_id = int(account[0][3:-1]) if '!' in account[0] else int(account[0][2:-1])
			account_member = ctx.guild.get_member(account_id)
			if account_member is None:
				notfound_embed = discord.Embed(title='Error!', description='User not found!', color=discord.Color.red())
				await ctx.send('', embed=notfound_embed)
				return
		else:
			account_member = ctx.author
		
		account_name = account_member.name
		
		with open('user.json', 'r') as f:
			users = json.load(f)
		
		try:
			bal_embed = discord.Embed(title=f'{account_name}\'s Balance', description=f'{str(users[account_name]["balance"])} milk units', color=discord.Color.green())
			await ctx.send('', embed=bal_embed)
		except KeyError:
			add_user_to_milk(account_name)

			with open('user.json', 'w') as f:
				json.dump(users, f, indent=4)
			
			bal = discord.Embed(title=f'{account_name}\'s Balance', description='0 milk units', color=discord.Color.green())
			await ctx.send('', embed=bal)

	@commands.command(name='daily')
	async def daily_claim(self, ctx):
		"""Description:
		Claim a 1000 milk unit reward every day!
		
		Use:
		`%sdaily`"""
		
		if not await is_on_cooldown(ctx, 86400, 'daily'):
			edit_user_milk(ctx.author.name, 1000)
			embed = discord.Embed(title='You have received 1000 milk units!', description='Come back in 24 hours for another reward.', color=discord.Color.purple())
			await ctx.send('', embed=embed)

	@commands.command()
	async def work(self, ctx, *args):
		"""Description:
		Work at your job or choose a new job.
		
		Use:
		`%swork [job | list]`"""

		with open('user.json', 'r') as f:
			users = json.load(f)

		if ctx.author.name not in users:
			add_user_to_milk(ctx.author.name)
			with open('user.json', 'r') as f:
				users = json.load(f)
		
		if args:
			if args[0] == 'list':
				jobs = '\n\n'.join([job.name + ' - ' + str(job.salary) + f'mu\n({self.job_aliases[self.job_list.index(job)]})' for job in self.job_list])

				embed = discord.Embed(title=f'Use `{self.prefix}work [job]` to choose a job.', description=jobs, color=discord.Color.green())
				await ctx.send('', embed=embed)
				return
			
			job = ' '.join(args)

			if job.lower() in self.job_names_lower or job.lower() in self.job_aliases_lower:
				if job.lower() in self.job_aliases_lower:
					job = self.job_names[self.job_aliases.index(job.upper())]
				else:
					job = self.job_names[self.job_names_lower.index(job.lower())]

				users[ctx.author.name]['job'] = job
				with open('user.json', 'w') as f:
					json.dump(users, f, indent=4)

				embed = discord.Embed(title=f'You are now working at {job}!', color=discord.Color.green())
				await ctx.send('', embed=embed)

			else:
				embed = discord.Embed(title='This job does not exist.', color=discord.Color.red())
				await ctx.send('', embed=embed)
		
		else:
			if not await is_on_cooldown(ctx, 3600, 'work_cd'):
				job = users[ctx.author.name]['job']
				
				if job == 'Simmons Gaming Industries':
					await self.gaming(ctx)

				elif job == 'Kangaroo Containment Facility':
					await self.kangaroo(ctx)
				
				else:
					embed = discord.Embed(title='You dont\'t have a job yet.', description='Use `.work list` to see a list of jobs.', color=discord.Color.red())
					await ctx.send('', embed=embed)

					users[ctx.author.name]['work_cd'] = 0.0
					with open('user.json', 'w') as f:
						json.dump(users, f, indent=4)

	@commands.command()
	async def shop(self, ctx):
		'''Description:
		Bring up a shop menu to buy items.
		Use:
		`%sshop`'''
		shop_embed = discord.Embed(title='Shop', description='\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_', color=discord.Color.purple())

		for shopitem in self.items:
			cost = int_to_str(shopitem.cost)
			shop_embed.add_field(name=f'{shopitem.emoji} {shopitem.name} - {cost}mu', 
				value=shopitem.description, 
				inline=False)
		
		await ctx.send('', embed=shop_embed)

	@commands.command()
	async def info(self, ctx, *item):
		'''Description:
		Bring up a detailed description of an item.
		Use:
		`%sinfo {item}'''

		if not item:
			embed = discord.Embed(title='You have not specified an item.', color=discord.Color.red())
			await ctx.send('', embed=embed)
			return

		if item.lower() in item_strs:
			item_idx = item_strs.index(item.lower())
			it = items[item_idx]

			cost = int_to_str(it.cost)

			details_embed = discord.Embed(title=f'{it.emoji} {it.name} - {cost}mu', description=it.detailed_description, color=discord.Color.green())
			await ctx.send('', embed=details_embed)

		else:
			embed = discord.Embed(title='Error!', description='Couldn\'t find this item', color=discord.Color.red())
			await ctx.send('', embed=embed)

	@commands.command()
	async def buy(self, ctx, *item):
		'''Description:
		Buy items from the shop.
		Use:
		`%sbuy {item}`'''

		if not item:
			embed = discord.Embed(title='You have not specified an item to buy.', color=discord.Color.red())
			await ctx.send('', embed=embed)
			return
		
		if item.lower() in item_strs:
			item_idx = item_strs.index(item.lower())
			it = self.items[item_idx]

			with open('user.json', 'r') as f:
				users = json.load(f)
			
			if ctx.author.name not in users:
				add_user_to_milk(ctx.author.name)
				with open('user.json', 'r') as f:
					users = json.load(f)
			
			if users[ctx.author.name]['balance'] >= it.cost:
				edit_user_milk(ctx.author.name, -it.cost)

				article = 'an' if it.name.startswith(('a', 'e', 'i', 'o', 'u')) else 'a'
				bought_embed = discord.Embed(title=f'You have bought {article} {it.name}', color=discord.Color.green())
				await ctx.send('', embed=bought_embed)
				
				if it in users[ctx.author.name]['items']:
					users[ctx.author.name]['items'][it] += 1
				else:
					users[ctx.author.name]['items'][it] = 0
				
				with open('user.json', 'w') as f:
					json.dump(users, f, indent=4)
			
			else:
				embed = discord.Embed(title='You do not have enough milk units to buy this item.', color=discord.Color.red())

		else:
			embed = discord.Embed(title='Error!', description='Item not found', color=discord.Color.red())
			await ctx.send('', embed=embed)

	@commands.command()
	async def inventory(self, ctx):
		'''Description:
		Bring up a display with all your items.
		Use:
		`%sinventory`'''

		inv_embed = discord.Embed(title=f'{ctx.author.name}\'s Inventory', description='\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_', color=discord.Color.purple())
		
		with open('user.json', 'r') as f:
			users = json.load(f)

		if ctx.author.name not in users:
			add_user_to_milk(ctx.author.name)
			with open('user.json', 'r') as f:
				users = json.load(f)

		for item, amount in enumerate(users[ctx.author.name]['items']):
			it = self.items[self.item_strs.index(item)]
			inv_embed.add_field(name=f'{it.emoji} {it.name} - {amount}', value=it.description, inline=False)
		
		await ctx.send('', embed=inv_embed)