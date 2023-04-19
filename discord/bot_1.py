# ---- discord/bot_1.py ----
# where main discord interfacing commands for bot_1 will be located

# default python imports
from random import randint
from traceback import format_exc
import asyncio
from itertools import cycle
import os
import ctypes
from datetime import datetime, timedelta
import atexit

# proprietary imports
from configs.config import CURRENCY_EMOJI
from market.economy import Market
from configs.config import logger,debug_vars

# discord APIs
import interactions
import discord
import nextcord
from nextcord.ext import commands, tasks
from nextcord import Permissions

# set up cmd to be pretty
ctypes.windll.kernel32.SetConsoleTitleW("discord bots")
os.system("mode con cols=85 lines=55")
# clear console
def Clear():
    os.system('cls')
Clear()

# bot init set up
with open("tokens/bot_1.0", "r", encoding="utf-8") as f:
    token = f.read()
commando = interactions.Client(token)
intents = nextcord.Intents.all()
client = commands.Bot(command_prefix = "/", intents=intents)
client.remove_command('help')

# ---- bot settings ----
# change the bot's status. add to list to have it cycle through
status = cycle(['Welcome to <server>!','Enjoy your stay at <server>!','For bot support contact Not mad, just disappointed#1881'])
#change background color of embeds
embed_color = 0xff3073

# make output more verbose
DEBUG = False

# basic commands for more assistive console outputs
def info(mes):
    print(f'INFO: {mes}')
def error(mes):
    print(f'ERROR: !!{mes}!!')

# code to run on exit to save new data
def save_and_push_data():
    os.system('cmd /k "git add *.json"')
    os.system('cmd /c "git commit -m "uploading data before local termination""')
atexit.register(save_and_push_data)


mar = Market()

# once connected to discord, print feedback
@client.event
async def on_ready():
    change_status.start()
    #startup msgs
    print('Bot_1 online---')

# where status cycling takes place. do not touch.
# if you want to change cycling statuses, search for "status = cycle([...])"
@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=next(status)))



# chat activities class
class message_monster():
    '''
    This class handles all functions pertaining to chat events (drops, claims, track active chatters)
    '''
    def __init__(self):
        self.client = client
        # guild.categories
        self.blacklisted_categories = [
            11002691264464027709,
            955349097005600808,
            955349137786814484,
            1002696320856887446,
            955350608649547786,
            955350669718601768,
            979288443588837426
        ]
        self.active_users = {}
        self.last_drop = datetime.now() - timedelta(days=1)
        self.active_drop = []


    async def activity(self,ctx):
        self.add_active(ctx)
        await self.remove_active()
        if datetime.now() >= self.last_drop + timedelta(minutes=10):
            for channel in list(self.active_users.keys()):
                if len(self.active_users[channel]) >= 5:
                    await self.drop(ctx)
                    break

    
    async def drop(self, message):
        self.last_drop = datetime.now()
        channel_id = int(message.channel.id)
        message_id = await message.channel.send(f'a wallet was just dropped. Pick it up with `$claim` to get some free {CURRENCY_EMOJI}')
        self.active_drop = [channel_id,int(message_id.id)]
        while datetime.now() <= self.last_drop + timedelta(minutes=2):
            if self.active_drop == []:
                return
            await asyncio.sleep(1)
        if self.active_drop != []:
            channel = await client.fetch_channel(self.active_drop[0])
            message = await channel.fetch_message(self.active_drop[1])
            self.active_drop = []
            await channel.delete_messages([message])

    async def claim_drop(self, ctx):
        if self.active_drop != []:
            username = ctx.author.username
            lotto = randint(1,100)
            if lotto == 77:
                info(f'{username} won the lotto')
                amount = 333
            else:
                amount = randint(10,35)
            await ctx.send(f'{username} picked up {amount} {CURRENCY_EMOJI}')
            mar.cheat_money(ctx.author.id, amount)
            self.active_drop = []
            return
    
    # forces drop in current chat
    async def cheat_drop(self,ctx):
        # TODO: add admin check
        await self.drop(ctx)

    # adds active chatters and text channels to list
    def add_active(self, message):
        channel_id = str(message.channel.id)
        channel_name = message.channel.name
        user_id = str(message.author.id)
        username = message.author.display_name
        if channel_id not in self.active_users:
            if DEBUG:
                info(f'New activity in {channel_name}.')
            self.active_users[channel_id] = {}
        if user_id not in self.active_users[channel_id]:
            if DEBUG:
                info(f'User {username} is now active in {channel_name}.')
        self.active_users[channel_id][user_id] = [datetime.now(),username,channel_name]

    # removes inactive chatters and text channels from list
    async def remove_active(self):
        channel_del = []
        for channel in list(self.active_users.keys()):
            user_del = []
            for user in list(self.active_users[channel].keys()):
                if self.active_users[channel][user][0] + timedelta(minutes=5) <= datetime.now():
                    if DEBUG:
                        info(f'User {self.active_users[channel][user][1]} is no longer active in {self.active_users[channel][user][2]}.')
                    user_del.append(user)
            for inactive in user_del:
                del self.active_users[channel][inactive]
            if len(self.active_users[channel]) == 0:
                channel_del.append(channel)
        for inactive in channel_del:
            try:
                del self.active_users[inactive]
            except Exception as e:
                error(f'could not remove channel from active list. {e} - {format_exc()}')


db = debug_vars(debug=DEBUG)
mm = message_monster()

"""
=======================================================================================
COMMANDS
=======================================================================================
    - Perms
    - Account Interactions
    - Store
    - Debugging
    - Helper Functions
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""


"""
    ****    PERMS   ****
"""
# add admins to bot
@commando.command(
    name="op",
    description="Give a user OP privileges",
    options = [
        interactions.Option(
            name="user_id",
            description="The ID of the user you want to OP",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
    ],
)
async def op(ctx:interactions.CommandContext, user_id):
    if db.get_debug():
        await debug(ctx)
    author = ctx.author.id
    username = ''.join([mem.username for mem in ctx.guild.get_all_members() if mem.id == user_id])
    if author not in mar.get_perms_list()['whitelist']:
        return error('user not authorized to use command')
    info(f'giving admin for {username}')
    result = mar.give_admin(int(user_id))
    if result[0]:
        await ctx.send(f'{username} is now oped')
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])

# remove admin
@commando.command(
    name="unop",
    description="Remove a user's OP privileges",
    options = [
        interactions.Option(
            name="user_id",
            description="The ID of the user you want to remove OP from",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
    ],
)
async def unop(ctx:interactions.CommandContext, user_id):
    if db.get_debug():
        await debug(ctx)
    author = ctx.author.id
    username = ''.join([mem.username for mem in ctx.guild.get_all_members() if mem.id == user_id])
    if author not in mar.get_perms_list()['whitelist']:
        return error('user not authorized to use command')
    info(f'giving admin for {username}')
    result = mar.remove_admin(int(user_id))
    if result[0]:
        await ctx.send(f'{username} is now unoped')
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])

# ban people from bot access
@commando.command(
    name="blacklist",
    description="Completely remove bot use for a user",
    options = [
        interactions.Option(
            name="user_id",
            description="The ID of the user you want to remove usage from",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
    ],
)
async def blacklist(ctx:interactions.CommandContext, user_id):
    if db.get_debug():
        await debug(ctx)
    author = ctx.author.id
    username = ''.join([mem.username for mem in ctx.guild.get_all_members() if mem.id == user_id])
    if author not in mar.get_perms_list()['whitelist']:
        return error('user not authorized to use command')
    info(f'giving admin for {username}')
    result = mar.blacklist(int(user_id))
    info(result)
    if result[0]:
        await ctx.send(f'{username} is now blacklisted')
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])

# remove bot banning
@commando.command(
    name="unblacklist",
    description="Remove user from bot blacklist",
    options = [
        interactions.Option(
            name="user_id",
            description="The ID of the user you want to give usage to",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
    ],
)
async def unblacklist(ctx:interactions.CommandContext, user_id):
    if db.get_debug():
        await debug(ctx)
    author = ctx.author.id
    username = ''.join([mem.username for mem in ctx.guild.get_all_members() if mem.id == user_id])
    if author not in mar.get_perms_list()['whitelist']:
        return error('user not authorized to use command')
    info(f'giving admin for {username}')
    result = mar.remove_blacklist(int(user_id))
    if result[0]:
        await ctx.send(f'{username} is now unblacklisted')
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])

# add money to account
@commando.command(
    name="cheat",
    description="Cheat in money, must be OP to use",
    options = [
        interactions.Option(
            name="amount",
            description="The amount of money you're cheating in",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
    ],
)
async def cheat(ctx:interactions.CommandContext, amount):
    if db.get_debug():
        await debug(ctx)
    user_id = ctx.author.id
    if user_id not in mar.get_perms_list()['whitelist']:
        return error('user not authorized to use command')
    info(f'cheating ${amount} for {ctx.author.name}')
    result = mar.cheat_money(user_id,int(amount))
    if result[0]:
        await ctx.send(f'{ctx.author.name} cheated in {amount} {CURRENCY_EMOJI}')
        mes = f'{ctx.author.name} now has ${mar.get_user_balance(user_id)[1]}'
        info(mes)
        if db.get_verbose():
            await ctx.send(mes)
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])


"""
    ****    ACCOUNT_INTERACTIONS   ****
"""
# creates a user account. should be done automatically when user joins/interacts with server but can be created manually (good for existing members)
@commando.command(
    name="create",
    description="Creates an account on the bot for the user, should never be needed to be used",
)
async def create(ctx:interactions.CommandContext):
    if db.get_debug():
        await debug(ctx)
    info(f'Creating file for {ctx.author.name}')
    user_id = ctx.author.id
    await ctx.send(mar.create_user(user_id)[1])

# delete user accounts
@commando.command(
    name="delete",
    description="Deletes an account on the bot",
    options = [
        interactions.Option(
            name="user_id",
            description="The ID of the user you want to delete",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
    ],
)
async def delete(ctx:interactions.CommandContext, user_id):
    if db.get_debug():
        await debug(ctx)
    info(f'Deleting file for {ctx.author.name}')
    result = mar.delete_user(user_id)
    if result[0]:
        await ctx.send(f'{user_id} account deleted successfully')
        info(f'{user_id} account deleted successfully')
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])

# cheats in small amount of money for other user
@commando.command(
    name="bless",
    description="Mysteriously generates money for another user of your choosing",
    options = [
        interactions.Option(
            name="recipient",
            description="Ping of the person you're wanting to bless",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def bless(ctx:interactions.CommandContext, recipient):
    if db.get_debug():
        await debug(ctx)
    giver_id = ctx.author.id
    receiver_id =  int(recipient[2:-1])
    recipient_username = ''.join([mem.username for mem in ctx.guild.get_all_members() if mem.id == receiver_id])
    if giver_id is receiver_id:
        info('user tried to bless their self')
        await ctx.send(f'You can\'t bless yourself. Try spreading a blessing to someone else :)')
        return None

    amount = randint(1,20)
    info(f'blessing {receiver_id} ${amount}')
    result = mar.cheat_money(receiver_id, int(amount))
    if result[0]:
        await ctx.send(f'You have blessed {recipient_username}. They\'ve received {amount} {CURRENCY_EMOJI}!')
        mes = f'The recipient now has ${mar.get_user_balance(receiver_id)[1]}'
        info(mes)
        if db.get_verbose():
            await ctx.send(mes)
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])

# claim event drop
@commando.command(
    name="claim",
    description="Claim a random active event drop",
)
async def claim(ctx:interactions.CommandContext):
    await mm.claim_drop(ctx.message)

# gamble 
@commando.command(
    name="coinflip",
    description="Gamble your money on a 50/50 coin flip, feeling lucky?",
    options = [
        interactions.Option(
            name="amount",
            description="The amount of currency you're willing to wager",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
    ],
)
async def coinflip(ctx:interactions.CommandContext, amount):
    amount = int(amount)
    if db.get_debug():
        await debug(ctx)
    author = ctx.author.id
    if mar.get_user_balance(author)[0]:
        if mar.get_user_balance(author)[1] < amount:
            await ctx.send(f'You don\'t have enough money to gamble {amount} {CURRENCY_EMOJI}. Your balance is {mar.get_user_balance(author)[1]}')
            return
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])
        return
    flip = randint(1,29)
    info(f'Gambling ${amount} from {ctx.author.name}')
    if flip % 2 == 1:
        result = mar.cheat_money(author, int(amount))
        if result[0]:
            await ctx.send(f'You have won {amount} {CURRENCY_EMOJI}! Your new balance is {mar.get_user_balance(author)[1]} {CURRENCY_EMOJI}!')
        else:
            if db.get_verbose():
                await ctx.send(result[1])
            error(result[1])
    else:
        result = mar.lose_money(author, int(amount))
        if result[0]:
            await ctx.send(f'You have lost {amount} {CURRENCY_EMOJI}. Your new balance is {mar.get_user_balance(author)[1]} {CURRENCY_EMOJI}!')
        else:
            if db.get_verbose():
                await ctx.send(result[1])
            error(result[1])

@commando.command(
    name="give",
    description="Gift away your hard earned currency",
    options = [
        interactions.Option(
            name="recipient",
            description="The ping of the person you want to give money to",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="amount",
            description="The amount of currency you're willing to give away",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
    ],
)
async def give(ctx:interactions.CommandContext, recipient, amount):
    if db.get_debug():
        await debug(ctx)
    giver_id = ctx.author.id
    receiver_id =  int(recipient[2:-1])
    recipient_username = ''.join([mem.username for mem in ctx.guild.get_all_members() if mem.id == receiver_id])
    info(f'giving {recipient_username} ${amount} from {ctx.author.name}')
    result = mar.give_money(giver_id, receiver_id, int(amount))
    if result[0]:
        await ctx.send(f'{ctx.author.name} gifted {recipient} {amount} {CURRENCY_EMOJI}.')
        mes = f'{ctx.author.name} now has ${mar.get_user_balance(giver_id)[1]}. The recipient now has ${mar.get_user_balance(receiver_id)[1]}'
        info(mes)
        if db.get_verbose():
            await ctx.send(mes)
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])

@commando.command(
    name="bal",
    description="Check your balance",
)
async def bal(ctx:interactions.CommandContext):
    if db.get_debug():
        await debug(ctx)
    user_id = ctx.author.id
    info(f'Getting balance for {ctx.author.name}')
    result = mar.get_user_balance(user_id)
    if result[0]:
        await ctx.send(f'{ctx.author.name} has {result[1]} {CURRENCY_EMOJI}.')
        info(f'{ctx.author.name} checked their balance and has ${result[1]}.')
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])

@commando.command(
    name="activate",
    description="Activate items from your inventory",
    options = [
        interactions.Option(
            name="item_name",
            description="The name of the item you are wanting to equip/activate",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def activate(ctx:interactions.CommandContext,item_name):
    if db.get_debug():
        await debug(ctx)
    author = ctx.author.id
    info(f'{ctx.author.name} is activating {item_name} from inventory')
    result = mar.activate_item(author,item_name)
    if result[0]:
        await role_activation(ctx,result[1])
        info(result[1])
        await ctx.send(f'{item_name} activated for {ctx.author.name}')
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])

@commando.command(
    name="deactivate",
    description="Deactivate items from your inventory",
    options = [
        interactions.Option(
            name="item_name",
            description="The name of the item you are wanting to unequip/deactivate",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def deactivate(ctx:interactions.CommandContext,*args):
    item_name = ''
    for x in args:
        item_name += f'{x} '
    item_name = item_name[:-1]
    if db.get_debug():
        await debug(ctx)
    author = ctx.author.id
    info(f'{ctx.author.name} is deactivating {item_name} from inventory')
    result = mar.deactivate_item(author,item_name)
    if result[0]:
        await role_deactivation(ctx,result[1])
        info(result[1])
        await ctx.send(f'{item_name} deactivated for {ctx.author.name}')
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])


"""
    ****    STORE   ****
"""
@commando.command(
    name="shop",
    description="View this server's shop"
)
async def shop(ctx:interactions.CommandContext):
    info(f'Gathering store info')
    if db.get_debug():
        await debug(ctx)
    
    result = mar.show_goods()
    if result[0]:
        embed = interactions.Embed(
            color=embed_color,
            title=f'{ctx.guild.name}\'s Shop',
            description=f'buy an item using `$buy [ item name / item no. ]`\n· · - ┈┈━━━━ ˚ . ✿ . ˚ ━━━━┈┈ - · ·',
        )
        embed.set_thumbnail(url=ctx.guild.icon_url)
        for x,item in enumerate(result[1]):
            role = "\n**|    **• Role: <@&{}>".format(result[1][item]["role"]) if result[1][item]["role"] != None else ""
            description = f'**|    **• {result[1][item]["description"]}{role}'
            embed.add_field(
                name=f'{x+1}\t\t{CURRENCY_EMOJI}{result[1][item]["price"]} • {item}',
                value= description,
                inline=False
            )
        await ctx.send(embeds=[embed])
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])


@commando.command(
    name="add_item",
    description="add item to shop",
    options = [
        interactions.Option(
            name="item_name",
            description="name of item to add",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="price",
            description="price in store",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
        interactions.Option(
            name="description",
            description="description of the added item",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="role",
            description="ID of role if item is a role",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
        interactions.Option(
            name="toggle",
            description="can the item be toggled? ",
            type=interactions.OptionType.BOOLEAN,
            required=True,
        ),
    ],
)
async def add_item(ctx:interactions.CommandContext,item_name,price,description,role=None,toggle=True):
    if db.get_debug():
        await debug(ctx)
    # check message author is whitelisted
    author = ctx.author.id
    if author not in mar.get_perms_list()['whitelist']:
        return error('user not authorized to use command')
    info(f'Adding item {item_name} to store')
    price = int(price)
    if toggle.lower() == 'false':
        toggle = False
    else:
        toggle = True
    result = mar.add_item(item_name,price,description,role if isinstance(role,int) else role[3:-1],toggle)
    if result[0]:
        await ctx.send(f'Added item {item_name} to store for {price} {CURRENCY_EMOJI}.')
        mes = f'{item_name} added to shop.\n{mar.show_goods()[1][item_name]}'
        info(mes)
        if db.get_verbose():
            await ctx.send(mes)
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])

@commando.command(
    name="edit_item",
    description="edit item in the shop",
    options = [
        interactions.Option(
            name="item_name",
            description="new name of item",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="price",
            description="new price in store",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
        interactions.Option(
            name="description",
            description="new description of the item",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="role",
            description="ID of role if item is a role",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
        interactions.Option(
            name="toggle",
            description="can the item be toggled?",
            type=interactions.OptionType.BOOLEAN,
            required=True,
        ),
    ],
)
async def edit_item(ctx:interactions.CommandContext,item_name,price,description,role=None,toggle=''):
    if db.get_debug():
        await debug(ctx)
    author = ctx.author.id
    price = int(price)
    if toggle.lower() == 'false':
        toggle = False
    else:
        toggle = True

    if author not in mar.get_perms_list()['whitelist']:
        return error('user not authorized to use command')
    info(f'Editing item {item_name} in store')
    result = mar.edit_item(item_name,price,description,role if isinstance(role,int) else role[3:-1],toggle)
    if result[0]:
        await ctx.send(f'Edited item {item_name} in store.')
        mes = f'{item_name} edited in shop.\n{mar.show_goods()[1][result[1]]}'
        info(mes)
        if db.get_verbose():
            await ctx.send(mes)
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])

@commando.command(
    name="delete_item",
    description="delete item from store",
    options = [
        interactions.Option(
            name="item_name",
            description="name of item to delete from store",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def delete_item(ctx:interactions.CommandContext,item_name):
    if db.get_debug():
        await debug(ctx)
    author = ctx.author.id
    if author not in mar.get_perms_list()['whitelist']:
        return error('user not authorized to use command')
    info(f'Removing item {item_name} from store')
    result = mar.remove_item(item_name)
    if result[0]:
        await ctx.send(f'{item_name} removed from store.')
        info(f'{item_name} removed from store')
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])

@commando.command(
    name="buy",
    description="buy an item from the store",
    options = [
        interactions.Option(
            name="item_name",
            description="name of item to delete from store",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def buy(ctx:interactions.CommandContext,item_name):
    if db.get_debug():
        await debug(ctx)
    author = ctx.author.id
    info(f'{ctx.author.name} buying item {item_name} from store')
    result = mar.buy_item(author,item_name)
    if result[0]:
        await role_activation(ctx,result[1])
        await ctx.send(f'{item_name} successfully bought, activated and added to inventory.')
        mes = f'{ctx.author.name} has a remanding balance of {mar.get_user_balance(author)[1]}.\n{mar.show_goods()[1][result[1]]}'
        info(mes)
        if db.get_verbose():
            await ctx.send(mes)
    else:
        if db.get_verbose():
            await ctx.send(result[1])
        error(result[1])


"""
    ****    DEBUGGING   ****
"""
@commando.command(
    name="debug",
    description="don't use unless you are Goo... its just annoying",
    options = [
        interactions.Option(
            name="message",
            description="message you want raw text from",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def debug(ctx:interactions.CommandContext):
    #prints message info to console
    message = ctx.message.content
    author = ctx.author.id
    mes = f'DEBUG RESPONSE:\nMessage received: {message}\nAuthor ID: {author}\nID type: {type(author)}\nGuild name: {ctx.guild}'
    info(mes)
    if db.get_verbose():
        await ctx.send(mes)

@commando.command(
    name="toggle_debug",
    description="makes A LOT more print in console",
)
async def toggle_debug(ctx:interactions.CommandContext):
    if db.get_debug():
        await debug(ctx)
    # toggle on/off responses for errors
    author = ctx.author.id
    if author not in mar.get_perms_list()['whitelist']:
        return error('user not authorized to use command')
    info(f'Enabling debug responses')
    db.set_debug(False) if db.get_debug() else db.set_debug(True) 
    status = 'enabled' if db.get_debug() else 'disabled'
    await ctx.send(f'Debug mode is {status}')

@commando.command(
    name="toggle_verbose",
    description="ESPECIALLY REALLY don't use unless you are Goo... prints all logs in console as responses",
)
async def toggle_verbose(ctx:interactions.CommandContext):
    if db.get_debug():
        await debug(ctx)
    # toggle on/off responses for errors
    author = ctx.author.id
    if author not in mar.get_perms_list()['whitelist']:
        return error('user not authorized to use command')
    info(f'Enabling verbose responses')
    db.set_verbose(False) if db.get_verbose() else db.set_verbose(True) 
    status = 'enabled' if db.get_verbose() else 'disabled'
    await ctx.send(f'Verbose mode is {status}')

@commando.command(
    name="cheat_drop",
    description="forces drop to spawn",
)
async def cheat_drop(ctx:interactions.CommandContext):
    if db.get_debug():
        await debug(ctx)
    # toggle on/off responses for errors
    author = ctx.author.id
    if author not in mar.get_perms_list()['whitelist']:
        return error('user not authorized to use command')
    await mm.cheat_drop(ctx.message)


"""
    ****    HELPER_FUNCTIONS   ****
"""

async def role_activation(ctx,item_name):
    author = ctx.author.id
    info(f'{ctx.author.name} activating {item_name} from inventory')
    result = mar.get_user_inventory(author)
    if result[0]:
        role_id = mar.get_role_id(author, item_name)
        if role_id[0]:
            if isinstance(role_id[1],int):
                role = nextcord.utils.get(ctx.guild.roles, id=role_id[1])
                await ctx.message.author.add_roles(role)
                info(f'successfully equipped role for user {ctx.author.name}')
            else:
                info(f'role for {item_name} == None, thus cannot activate role')

async def role_deactivation(ctx,item_name):
    author = ctx.author.id
    info(f'{ctx.author.name} activating {item_name} from inventory')
    result = mar.get_user_inventory(author)
    if result[0]:
        role_id = mar.get_role_id(author, item_name)
        if role_id[0]:
            if isinstance(role_id[1],int):
                role = nextcord.utils.get(ctx.guild.roles, id=role_id[1])
                await ctx.message.author.remove_roles(role)
                info(f'successfully unequipped role for user {ctx.author.name}')
            else:
                info(f'role for {item_name} == None, thus cannot deactivate role')

"""
=======================================================================================
END_COMMANDS
=======================================================================================
"""

@tasks.loop(seconds=60)
async def check_actives():
    await mm.remove_active()


loop = asyncio.get_event_loop()

task2 = loop.create_task(commando.start())
task1 = loop.create_task(client.run(token))

gathered = asyncio.gather(task1, task2, loop=loop)
loop.run_until_complete(gathered)