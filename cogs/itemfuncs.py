import discord, json

async def eat_cookie(ctx, user):
    embed = discord.Embed(title='You ate the cookie. Nothing happened...', color=discord.Color.blue())
    await ctx.send('', embed=embed)

async def drink_milk(ctx, user):
    with open('user.json', 'r') as f:
        users = json.load(f)
    
    users[user]['cdstate'] = 'off'
    
    with open('user.json', 'w') as f:
        json.dump(users, f, indent=4)

    embed = discord.Embed(title='You drank the milk carton. You feel power flowing through your veins.', description='Command cooldowns have been disabled.', color=discord.Color.green())
    await ctx.send('', embed=embed)

functions = [eat_cookie, drink_milk]