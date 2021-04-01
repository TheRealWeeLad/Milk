from Utils import (discord, random, asyncio, get_prefix, edit_user_milk, pre_gambling)
from discord.ext import commands

class Gambling(commands.Cog):
	"""Commands for gambling your milk"""

	prefix = '.'

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

	@commands.command(name='coinflip', aliases=['cf'])
	async def coin_flip(self, ctx, amount_to_bet, heads_or_tails):
		"""Description:
		Bet your milk on a coinflip
		
		Use:
		`%scoinflip {amount_to_bet} {heads_or_tails}`
		Aliases:
		`cf`"""
		bet = await pre_gambling(ctx, amount_to_bet)
		if bet is None:
			return
		
		flipping = discord.Embed(title=':coin: Flipping Coin...', color=discord.Color.gold())
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

	@commands.command(aliases=['bj'])
	@commands.cooldown(5, 3)
	@commands.bot_has_permissions(manage_messages=True)
	async def blackjack(self, ctx, amount_to_bet):
		"""Description:
		   Bet your milk to play Blackjack

		   Use:
		   `%sblackjack {amount_to_bet}`
		   Aliases:
		   `bj`"""
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

