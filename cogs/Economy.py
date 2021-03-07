import discord, json
from discord.ext import commands
from Utils import (random, asyncio, add_user_to_milk, edit_user_milk, is_on_cooldown)

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
		self.job_list = [Job('Simmons Gaming Industries', 250), Job('Cangaroo Containment Facility', 1000)]
		self.job_aliases = ['SGI', 'CCF']
		self.job_names = [job.name for job in self.job_list]

	@staticmethod
	def remove_exclamation_point(string):
		new_str = ''
		for char in string:
			if char == '!':
				continue
			new_str += char
		
		return new_str

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

		message = discord.Embed(title='Top 5 Milk Owners', description=desc, color=0xffff00)
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
		
		if args:
			if args[0] == 'list':
				jobs = '\n\n'.join([job.name + ' - ' + str(job.salary) + f'mu\n({self.job_aliases[self.job_list.index(job)]})' for job in self.job_list])

				embed = discord.Embed(title=f'Use `{self.prefix}work [job]` to choose a job.', description=jobs, color=discord.Color.green())
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
			if not await is_on_cooldown(ctx, 3600, 'work_cd'):
				job = users[ctx.author.name]['job']
				
				if job == 'Simmons Gaming Industries':
					pass

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
					canga_row += 1
					canga_column += 1

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
					instructions_msg = await ctx.send('', embed=instructions_embed)

					def check(message, author):
						return message.author == author

					try:
						msg = await self.bot.wait_for('message', check=lambda m: check(m, ctx.author), timeout=3)
					
					except asyncio.TimeoutError:
						embed = discord.Embed(title='Too late!', description='The Cangaroo escaped before you could catch it. Try again next time.', color=discord.Color.red())
						await instructions_msg.edit(embed=embed)

					else:
						if msg.content == str(canga_row) + ' ' + str(canga_column):
							embed = discord.Embed(title='Good job! You caught the Cangaroo before it could escape. You have received 250mu', color=discord.Color.green())
							edit_user_milk(msg.author.name, 250)
						else:
							embed = discord.Embed(title='Too bad! You couldn\'t catch the Cangaroo before it escaped. Try again next time.', color=discord.Color.red())

						await ctx.send('', embed=embed)
				
				else:
					embed = discord.Embed(title='You dont\'t have a job yet.', description='Use `.work list` to see a list of jobs.', color=discord.Color.red())
					await ctx.send('', embed=embed)

					users[ctx.author.name]['work_cd'] = 0.0
					with open('user.json', 'w') as f:
						json.dump(users, f, indent=4)
