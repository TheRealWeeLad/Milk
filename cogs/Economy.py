import discord, json
from discord.ext import commands
from Utils import (get_users, dump_users, random, asyncio, add_user_to_milk, edit_user_milk, is_on_cooldown, int_to_str)
from itemfuncs import functions

class Item:
	def __init__(self, name: str, description: str, detailed_description: str, emoji: str, cost: int, function):
		self.name = name
		self.description = description
		self.detailed_description = detailed_description
		self.emoji = emoji
		self.cost = cost
		self.sellCost = round(self.cost * 0.75)
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

		cookie = Item('Cookie', 'Does nothing', 'Does literally nothing', ':cookie:', 5, functions[0])
		lt = Item('Lottery Ticket', 'Provides a small chance at winning big!', 'Using this item will grant you a very small change to win *100000*mu!', ':tickets:', 100, functions[3])
		shovel = Item('Shovel', f'Grants access to the `{self.prefix}dig` command', f'This item will allow you to dig in the calcium mines using the `{self.prefix}dig` command.', '<:shovel:832020414632165406>', 5000, functions[2])
		milk = Item('Milk Carton', 'Negates command cooldowns', 'Drinking this will allow you to use commands as much as you like without provoking a cooldown.', '<:carton:826231831757717516>', 999999, functions[1])
		self.items = [milk, shovel, lt, cookie]
		self.item_strs = list(map(lambda o: str(o).lower(), self.items))

	@staticmethod
	def remove_exclamation_point(string):
		l = list(string)
		
		while '!' in l:
			l.remove('!')

		return ''.join(l)

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
		users = get_users()
		
		balance_list = {}
		for user, val in users.items():
			balance_list[user] = val['balance']
		
		new_balances = sorted(balance_list.items(), key=lambda kv: kv[1], reverse=True)[:5]
		
		desc = ''
		for i in new_balances:
			bal = int_to_str(i[1])
			new_list = [i[0], bal]
			desc += ' - '.join(new_list) + 'mu' + '\n'

		message = discord.Embed(title='Top 5 Milk Owners', description=desc, color=discord.Color.gold())
		await ctx.send('', embed=message)

	@commands.command(name='balance', aliases=['bal'])
	async def check_balance(self, ctx, *account):
		"""Description:
		Check the amount of milk that you have acquired
		
		Use:
		`%sbalance [account_to_check]`
		Aliases:
		`bal`"""

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
		
		users = get_users()
		
		try:
			balance = int_to_str(users[account_member.name]['balance'])
			bal_embed = discord.Embed(title=f'{account_name}\'s Balance', description=f'{balance} milk units', color=discord.Color.green())
			await ctx.send('', embed=bal_embed)
		except KeyError:
			add_user_to_milk(account_name)
			
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

		users = get_users()

		if ctx.author.name not in users:
			add_user_to_milk(ctx.author.name)
			users = get_users()
		
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
				dump_users(users)

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
					dump_users(users)

	@commands.command()
	async def shop(self, ctx):
		'''Description:
		Bring up a shop menu to buy items.
		Use:
		`%sshop`'''
		shop_embed = discord.Embed(title='Shop', description=r'\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_', color=discord.Color.purple())

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
		`%sinfo {item}`'''

		if not item:
			embed = discord.Embed(title='You have not specified an item.', color=discord.Color.red())
			await ctx.send('', embed=embed)
			return

		item = ' '.join(item)

		if item.lower() in self.item_strs:
			item_idx = self.item_strs.index(item.lower())
			it = self.items[item_idx]

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
		`%sbuy {item} [amount]`'''

		if not item:
			embed = discord.Embed(title='You have not specified an item to buy.', color=discord.Color.red())
			await ctx.send('', embed=embed)
			return

		try:
			amount = int(item[-1])
			item = item[:-1]
		except ValueError:
			amount = 1
		
		item = ' '.join(item)

		if item.lower() in self.item_strs:
			item_idx = self.item_strs.index(item.lower())
			it = self.items[item_idx]

			users = get_users()
			
			if ctx.author.name not in users:
				add_user_to_milk(ctx.author.name)
				users = get_users()
			
			if users[ctx.author.name]['balance'] >= it.cost * amount:
				edit_user_milk(ctx.author.name, -it.cost * amount)
				users = get_users()

				if amount == 1:
					article = 'an' if it.name.startswith(('a', 'e', 'i', 'o', 'u')) else 'a'
					bought_embed = discord.Embed(title=f'You have bought {article} {it.name}', color=discord.Color.green())
				else:
					bought_embed = discord.Embed(title=f'You have bought {amount} {it.name}s', color=discord.Color.green())
				
				await ctx.send('', embed=bought_embed)
				
				if it.name in users[ctx.author.name]['items']:
					users[ctx.author.name]['items'][it.name] += amount
				else:
					users[ctx.author.name]['items'][it.name] = amount
				
				dump_users(users)
			
			else:
				embed = discord.Embed(title='You do not have enough milk units to buy this item.', color=discord.Color.red())
				await ctx.send('', embed=embed)

		else:
			embed = discord.Embed(title='Error!', description='Item not found', color=discord.Color.red())
			await ctx.send('', embed=embed)

	@commands.command(aliases=['inv'])
	async def inventory(self, ctx):
		'''Description:
		Bring up a display with all your items.
		Use:
		`%sinventory`
		Aliases:
		`inv`'''

		inv_embed = discord.Embed(title=f'{ctx.author.name}\'s Inventory', description=r'\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_', color=discord.Color.purple())
		
		users = get_users()

		if ctx.author.name not in users:
			add_user_to_milk(ctx.author.name)
			users = get_users()

		for item, amount in users[ctx.author.name]['items'].items():
			if item == 'calcium':
				inv_embed.add_field(name=f':rock: Calcium - {amount}', value='Mineral dug from the calcium mines.', inline=False)
				continue

			it = self.items[self.item_strs.index(item.lower())]
			inv_embed.add_field(name=f'{it.emoji} {it.name} - {amount}', value=it.description, inline=False)
		
		await ctx.send('', embed=inv_embed)

	@commands.command()
	async def use(self, ctx, *item):
		'''Description:
		Use an item in your inventory.
		Use:
		`%suse {item}`'''

		if not item:
			embed = discord.Embed(title='You have not specified an item to use.', color=discord.Color.red())
			await ctx.send('', embed=embed)
			return
		
		item = ' '.join(item)


		users = get_users()

		if ctx.author.name not in users:
			add_user_to_milk(ctx.author.name)
			users = get_users()

		if item.lower() in map(str.lower, users[ctx.author.name]['items']):
			it = self.items[self.item_strs.index(item.lower())]

			amount = users[ctx.author.name]['items'][it.name]

			if it.use == functions[2]:
				amount += 1

			if amount > 1:
				amount -= 1
				users[ctx.author.name]['items'][it.name] = amount
			else:
				del users[ctx.author.name]['items'][it.name]

			dump_users(users)
			
			if it.use == functions[3]:
				await it.use(ctx, ctx.author.name, self.bot)
			else:
				await it.use(ctx, ctx.author.name)

		else:
			embed = discord.Embed(title='Error!', description='You don\'t have this item or the item is invalid.', color=discord.Color.red())
			await ctx.send('', embed=embed)

	@commands.command()
	async def dig(self, ctx):
		'''Description:
		Dig in the calcium mines for calcium to sell.
		Use:
		`%sdig`'''

		users = get_users()
		
		if ctx.author.name not in users:
			add_user_to_milk(ctx.author.name)
			users = get_users
		
		if 'Shovel' not in users[ctx.author.name]['items']:
			embed = discord.Embed(title='You don\'t have a shovel to dig with!', color=discord.Color.red())
			await ctx.send('', embed=embed)
			return

		amount = random.randint(1, 200)

		outcome = random.randint(49, 50)

		if outcome < 50:
			embed = discord.Embed(title=f'You have successfully mined {amount}mg of calcium!', color=discord.Color.green())

			if 'calcium' not in users[ctx.author.name]['items']:
				users[ctx.author.name]['items']['calcium'] = amount

			else:
				users[ctx.author.name]['items']['calcium'] += amount
			
		else:
			embed = discord.Embed(title='Alas! Your shovel broke while mining.', description='You lost your shovel and didn\'t gain any calcium either.', color=discord.Color.red())

			if users[ctx.author.name]['items']['Shovel'] > 1:
				users[ctx.author.name]['items']['Shovel'] -= 1
			else:
				del users[ctx.author.name]['items']['Shovel']
		
		dump_users(users)

		await ctx.send('', embed=embed)
	
	@commands.command()
	async def sell(self, ctx, *item):
		"""Description:
		Sell your items for milk units.
		Use:
		`%ssell {item} [amount]`
		"""

		if not item:
			embed = discord.Embed(title='Error!', description='No item listed to sell.', color=discord.Color.red())
			await ctx.send('', embed=embed)
			return

		try:
			amount = int(item[-1])
			item = item[:-1]
		except ValueError:
			amount = 1

		if amount < 1:
			embed = discord.Embed(title='Error!', description='You can\'t sell fewer than 1 item.', color=discord.Color.red())
			await ctx.send('', embed=embed)
			return
		
		name = ' '.join(item)

		users = get_users()

		if ctx.author.name not in users:
			add_user_to_milk(ctx.author.name)
			users = get_users()

		items = users[ctx.author.name]['items']

		if name.lower() not in map(str.lower, items):
			embed = discord.Embed(title='Error!', description='You do not own this item.', color=discord.Color.red())
			await ctx.send('', embed=embed)
			return
		
		if name.lower() == 'calcium':
			if amount > items['calcium']:
				embed = discord.Embed(title='Error!', description='You can\'t sell more calcium than you have.', color=discord.Color.red())
				await ctx.send('', embed=embed)
				return
			
			items['calcium'] -= amount

			users[ctx.author.name]['balance'] += amount * 10

			embed = discord.Embed(title=f'You have successfully sold {amount}mg of calcium!', description=f'You have received {amount * 10}mu!', color=discord.Color.green())

			if items['calcium'] == 0:
				del items['calcium']

		else:
			item = self.items[self.item_strs.index(name.lower())]

			if amount > items[item.name]:
				embed = discord.Embed(title='Error!', description=f'You can\'t sell more {name}s than you have.', color=discord.Color.red())
				await ctx.send('', embed=embed)
				return

			items[item.name] -= amount
			users[ctx.author.name]['balance'] += item.sellCost * amount
			
			plural = 's' if amount > 1 else ''

			embed = discord.Embed(title=f'You have successfully sold {amount} {item.name}{plural}!', description=f'You have received {item.sellCost * amount}mu!', color=discord.Color.green())

			if items[item.name] == 0:
				del items[item.name]

		await ctx.send('', embed=embed)
		users[ctx.author.name]['items'] = items
		dump_users(users)
