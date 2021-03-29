def drink_milk(user):
    with open('user.json', 'r') as f:
        users = json.load(f)
    
    users[user]['cdstate'] = 'off'

    with open('user.json', 'w') as f:
        json.dump(users, f, indent=4)

functions = [drink_milk]