import discord, json
from discord.ext import commands

class Utilities(commands.Cog):
	"""Helpful commands"""

	prefix = '.'

	def __init__(self, bot):
		self.bot = bot
		self.emoji = ':wrench:'

	@commands.command(aliases=['commands'])
	async def help(self, ctx, *command):
		"""Description:
		Displays help message
		
		Use:
		`%shelp [command]`
		Aliases:
		`commands`"""
		if not command:
			halp=discord.Embed(title='Command Listing',
							description=f'Use `{self.prefix}help [command]` to find out more about them!',
							color=discord.Color.blue())
			for x in self.bot.cogs:
				cog = self.bot.cogs[x]
				cmds_str = ''
				for cmd in cog.get_commands():
					cmds_str += f'`{self.prefix}{cmd}` '
				halp.add_field(name=cog.emoji + x, value=cmds_str, inline=False)

			cmds_desc = ''
			for y in self.bot.commands:
				if not y.cog_name and not y.hidden:
					cmds_desc += ('{} - {}'.format(y.name.title(), y.help.format(self.prefix))+'\n')
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
							halp = discord.Embed(title=y.name.title() + ' Description', description=y.help % self.prefix, color=discord.Color.blue())

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
		`%sprefix {new_prefix}`"""
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
		`%sping`"""
		ping = ctx.message
		pong = await ctx.send('Ping is')
		delta = pong.created_at - ping.created_at
		delta = int(delta.total_seconds() * 1000)
		await pong.edit(content=f'Ping is {delta}ms\nLatency is {str(self.bot.latency * 1000)[:2]}ms')
