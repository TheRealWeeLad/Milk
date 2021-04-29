from Utils import (discord, json, random, get_users, dump_users, edit_user_milk)

async def eat_cookie(ctx, user):
    embed = discord.Embed(title='You ate the cookie. Nothing happened...', color=discord.Color.blue())
    await ctx.send('', embed=embed)

async def drink_milk(ctx, user):
    users = get_users()
    
    users[user]['cdstate'] = 'off'
    
    dump_users(users)

    embed = discord.Embed(title='You drank the milk carton. You feel power flowing through your veins.', description='Command cooldowns have been disabled.', color=discord.Color.green())
    await ctx.send('', embed=embed)

async def cant_be_used(ctx, user):
    embed = discord.Embed(title='Error!', description='This item can\'t be used.', color=discord.Color.red())
    await ctx.send('', embed=embed)

def check_lot_msg(msg):
    try:
        int(msg.content)
        return True
    except ValueError:
        return False

async def enter_lottery(ctx, user, bot):
    amount_embed = discord.Embed(title='How many would you like to use?', color=discord.Color.blue())
    await ctx.send('', embed=amount_embed)

    try:
        msg = await bot.wait_for('message', timeout=10, check=check_lot_msg)

        amount = int(msg.content)

        if amount < 1:
            embed = discord.Embed(title='Error!', description='You can\'t use fewer than 1 tickets.', color=discord.Color.red())
            await ctx.send('', embed=embed)
            return

        users = get_users()

        if amount > users[ctx.author.name]['items']['Lottery Ticket'] + 1:
            embed = discord.Embed(title='Error!', description='You dont\'t have this many tickets.', color=discord.Color.red())
            await ctx.send('', embed=embed)
            users[ctx.author.name]['items']['Lottery Ticket'] += 1
            dump_users(users)
            return

        num_list = [random.randint(1, 200) for _ in range(amount)]

        if 69 in num_list:
            edit_user_milk(ctx.author.name, 100000)

            embed = discord.Embed(title='You won!', description='You have received 100000mu!', color=discord.Color.green())
            await ctx.send('', embed=embed)

        else:
            embed = discord.Embed(title='You lost.', description='Better luck next time.', color=discord.Color.red())
            await ctx.send('', embed=embed)

        users[ctx.author.name]['items']['Lottery Ticket'] -= (amount - 1)

        if users[ctx.author.name]['items']['Lottery Ticket'] == 0:
            del users[ctx.author.name]['items']['Lottery Ticket']

        dump_users(users)
    
    except asyncio.TimeoutError:
        embed = discord.Embed(title='Timed out.', description='You didn\'t respond in time.', color=discord.Color.red())
        await ctx.send('', embed=embed)
        users = get_users()
        users[ctx.author.name]['items']['Lottery Ticket'] += 1
        dump_users(users)

functions = [eat_cookie, drink_milk, cant_be_used, enter_lottery]