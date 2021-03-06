from Utils import (discord, time, asyncio, get_prefix)
from discord.ext import commands

class Games(commands.Cog):
    """Commands that allow you to play different games"""

    def __init__(self, bot):
        self.bot = bot
        self.emoji = ':video_game:'
        self.playingHangman = False
        self.player_index = 1

    @commands.command()
    @commands.cooldown(1, 10)
    async def hangman(self, ctx):
        """Description:
        Play hangman with up to 3 other people.
        
        Use:
        %shangman"""

        if self.playingHangman:
            embed = discord.Embed(title='There is already a hangman game going on!', description='Please wait until the current hangman game is finished.', color=discord.Color.red())
            await ctx.send('', embed=embed)
            return

        self.playingHangman = True

        players = [ctx.author.name]
        self.player_index = 1
        start_time = time.time()

        join_embed = discord.Embed(title='A hangman game is starting! React with :white_check_mark: to start the game.', description=f'React to this message with :nazar_amulet: to join the game. React with :door: to leave the game.\n(The game will be aborted in 30sec)\n\nPlayers: {players[0]}', color=discord.Color.blue())
        join_msg = await ctx.send('', embed=join_embed)
        await join_msg.add_reaction('✅')
        await join_msg.add_reaction('🧿')
        await join_msg.add_reaction('🚪')

        def check(reaction, user):
            if user.id != self.bot.user.id and user.id != ctx.author.id:
                if reaction.emoji == '🧿' and user.name not in players and len(players) <= 4:
                    join_embed.description += f', {players[self.player_index]}'
                    self.player_index += 1
                    players.append(user.name)
                    return True
                elif reaction.emoji == '🚪' and user.name in players:
                    players.remove(user.name)
                    return True
            elif user.id == ctx.author.id:
                if reaction.emoji == '✅':
                    return True
            return False

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=30, check=check)
            
            while reaction.emoji != '✅':
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=30 - (time.time() - start_time), check=check)
                await join_msg.edit(embed=join_embed)

        except asyncio.TimeoutError:
            embed = discord.Embed(title='The game has been aborted.', description=f'Use `{get_prefix(None, ctx)}hangman` to start another game.', color=discord.Color.red())
            await join_msg.edit(embed=embed)
            self.playingHangman = False
            return

        await ctx.author.send('Tell me what to make the hidden message.')

        def check_msg(message):
            return message.channel.type == discord.ChannelType.private and message.author.name != self.bot.user.name

        while True:
            msg = await self.bot.wait_for('message', timeout=60, check=check_msg)
            message = msg.content

            if len(message) > 30:
                await ctx.author.send('This message is too long. Try another one.')
            else:
                break

        await ctx.author.send('This message has been accepted.')
        
        hidden_word = ' '.join(['_' * len(word) for word in message.split()])
        hidden_str = ' '.join([r'\_ ' * len(word) for word in message.split()])

        hidden_embed = discord.Embed(title=hidden_str, description='Wrong Guesses: 0/5', color=discord.Color.blue())
        hidden_msg = await ctx.send('', embed=hidden_embed)

        def check_guess(msg):
            return len(msg.content) == 1 and msg.author.name in players

        guessed_letters = []
        wrong_guesses = 0

        end_result = ' '.join(list(message))

        while hidden_str != end_result:
            try:
                guess = await self.bot.wait_for('message', timeout=120, check=check_guess)

            except asyncio.TimeoutError:
                embed = discord.Embed(title='The game has been aborted.', description='Too much time has passed without a guess.', color=discord.Color.red())
                await hidden_msg.delete()
                await ctx.send('', embed=embed)
                self.playingHangman = False
                return
            
            guess = guess.content.lower()

            if guess not in guessed_letters:
                guessed_letters.append(guess)

                if guess in message.lower():
                    positions = []
                    appearances = 0
                    for char in message.lower():
                        if char == guess:
                            appearances += 1
                    
                    start = -1
                    for _ in range(appearances):
                        start = message.lower().find(guess, start + 1)
                        positions.append(start)
                    
                    hidden_word_list = list(hidden_word)

                    for pos in positions:
                        hidden_word_list[pos] = message[pos]

                    hidden_str = ''
                    for char in hidden_word_list:
                        if char == '_':
                            hidden_str += r'\_ '
                        else:
                            hidden_str += char + ' '

                    hidden_word = ''.join(hidden_word_list)
                    hidden_str = hidden_str[:-1]

                    await hidden_msg.delete()
                    hidden_embed.title = hidden_str

                    hidden_msg = await ctx.send('', embed=hidden_embed)

                else:
                    wrong_guesses += 1
                    
                    hidden_embed.description = f'Wrong Guesses: {wrong_guesses}/5'
                    await hidden_msg.delete()
                    hidden_msg = await ctx.send('', embed=hidden_embed)

                    if wrong_guesses == 5:
                        self.playingHangman = False

                        embed = discord.Embed(title='You lost!', description=f'The message was {message}', color=discord.Color.red())
                        await ctx.send('', embed=embed)
                        return
        
        embed = discord.Embed(title='You guessed the message! Good job! :thumbsup:', color=discord.Color.green())
        await ctx.send('', embed=embed)

        self.playingHangman = False