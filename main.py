import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import datetime
import os, random
import json
import requests, time
from bs4 import BeautifulSoup
import pythonping
import sys
from time import sleep
import wavelink

TOKEN = " BOT TOKEN "
GITUSER = " GITHUB USERNAME (THIS IS REQUIRED TO POST ISSUES FROM DISCORD TO GITHUB) "
GITPASS = " GITHUB PASSWORD (THIS IS REQUIRED TO POST ISSUES FROM DISCORD TO GITHUB) "
REPO_OWNER = "Shreyas-ITB"
REPO_NAME = "Packetee-Discord-Bot"
EXPLORER_STATS = "https://explorer.pkt.cash/api/v1/PKT/pkt/packetcrypt/stats"
EXPLORER_COIN = "https://explorer-api.pkt.ai/api/v1/PKT/pkt/stats/coins"
EXPLORER_DIFF = "https://explorer-api.pkt.ai/api/v1/PKT/pkt/chain/down/1"
global db
db = "database.json"
exchdb = "exchdb.json"
chatintents = discord.Intents.all()
bot = commands.Bot(command_prefix="pkt ", help_command=None, intents=chatintents, owner_id=859368295823835136)

market = [
    {"name":"Watch","price":50,"description":"Time"},
    {"name":"Phone","price":80,"description":"Call"},
    {"name":"Laptop","price":120,"description":"Work"},
    {"name":"PC","price":190,"description":"Gaming"},
    {"name":"iMac","price":240,"description":"Show off"},
    {"name":"iPhone","price":320,"description":"Privacy"},
    {"name":"MacBook","price":500,"description":"Insane M2 book"},
    {"name":"LargeVilla","price":780,"description":"House"},
    {"name":"MrBeast Studio","price":900,"description":"Youtube"},
    {"name":"La Ferrari","price":99999,"description":"Sports Car"}
    ]

@tasks.loop(seconds=5)
async def changeStatus():
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="with your money!"))
    await asyncio.sleep(3)
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="PktBoiss!"))
    await asyncio.sleep(3)
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.competing, name="Pkt Community!"))
    await asyncio.sleep(3)
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="Made by Shreyas-ITB"))
    await asyncio.sleep(3)
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="/help command"))
    await asyncio.sleep(3)

class colors:
    default = 0
    teal = 0x1abc9c
    dark_teal = 0x11806a
    green = 0x2ecc71
    dark_green = 0x1f8b4c
    blue = 0x3498db
    dark_blue = 0x206694
    purple = 0x9b59b6
    dark_purple = 0x71368a
    magenta = 0xe91e63
    dark_magenta = 0xad1457
    gold = 0xf1c40f
    dark_gold = 0xc27c0e
    orange = 0xe67e22
    dark_orange = 0xa84300
    red = 0xe74c3c
    dark_red = 0x992d22
    lighter_grey = 0x95a5a6
    dark_grey = 0x607d8b
    light_grey = 0x979c9f
    darker_grey = 0x546e7a
    blurple = 0x7289da
    greyple = 0x99aab5

def humanbytes(B):
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2) # 1,048,576
    GB = float(KB ** 3) # 1,073,741,824
    TB = float(KB ** 4) # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB/s'.format(B / KB)
    elif MB <= B < GB:
        return '{0:.2f} MB/s'.format(B / MB)
    elif GB <= B < TB:
        return '{0:.2f} GB/s'.format(B / GB)
    elif TB <= B:
        return '{0:.2f} TB/s'.format(B / TB)

def converttime(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
     
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def getstats():
    req = requests.get(EXPLORER_STATS)
    if req.status_code == 200:
        var = json.loads(req.content)
        bitspersec = var["results"][0]["bitsPerSecond"]
        encrypersec = var["results"][0]["encryptionsPerSecond"]
        return (encrypersec, bitspersec)
    else:
        return

def getcoinstats():
    req1 = requests.get(EXPLORER_COIN)
    if req1.status_code == 200:
        var1 = json.loads(req1.content)
        minedtodate = var1["alreadyMined"]
        reward = var1["reward"]
        return (minedtodate, reward)
    else:
        return

def getdiffstats():
    req2 = requests.get(EXPLORER_DIFF)
    if req2.status_code == 200:
        var2 = json.loads(req2.content)
        anndiff = var2["results"][0]["pcAnnDifficulty"]
        blkdiff = var2["results"][0]["pcBlkDifficulty"]
        return (anndiff, blkdiff)
    else:
        return

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    changeStatus.start()
    try:
        synced = await bot.tree.sync()
        print(f"Successfully Synced {len(synced)} commands..")
    except Exception:
        print("Failed to sync commands")
    print("Enabled status updates..")
    bot.loop.create_task(connect_nodes())
    global startTime
    startTime = time.time()
    print("------")

@bot.event
async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.Track, reason):
    if not player.queue.is_empty:
        next_track = player.queue.get()
        await player.play(next_track)

@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f'Node: <{node.identifier}> is ready!')

async def connect_nodes():
    await bot.wait_until_ready()
    await wavelink.NodePool.create_node(
        bot=bot,
        host='ssl.freelavalink.ga',
        port=443,
        password='www.freelavalink.ga',
        https=True
    )

async def open_account(user):
    users = await get_bank_data()
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0
    with open(db,'w') as f:
        json.dump(users,f)
    return True

async def get_bank_data():
    with open(db,'r') as f:
        users = json.load(f)
    return users

async def update_bank(user,change=0,mode = 'wallet'):
    users = await get_bank_data()
    users[str(user.id)][mode] += change
    with open(db,'w') as f:
        json.dump(users,f)
    bal = users[str(user.id)]['wallet'],users[str(user.id)]['bank']
    return bal

async def get_addrs():
    with open(exchdb,'r') as f:
        users = json.load(f)
    return users

async def del_addrs():
    with open(exchdb,'w') as f:
        f.seek(0)
        f.truncate()
        data = {}
        json.dump(data, f)
    return

async def exchangereq(user, address):
    users = await get_addrs()
    if str(user.name) in users:
        return False
    else:
        users[str(user.name)] = {}
        users[str(user.name)]["address"] = address
    with open(exchdb,'w') as f:
        json.dump(users,f, indent=4)
    return True

async def sell_this(user,item_name,amount,price = None):
    item_name = item_name.lower()
    name_ = None
    for item in market:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price==None:
                price = 0.7* item["price"]
            break
    if name_ == None:
        return [False,1]
    cost = price*amount
    users = await get_bank_data()
    bal = await update_bank(user)
    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False,2]
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            return [False,3]
    except:
        return [False,3]    
    with open(db,"w") as f:
        json.dump(users,f)
    await update_bank(user,cost,"wallet")
    return [True,"Worked"]

async def buy_this(user,item_name,amount):
    item_name = item_name.lower()
    name_ = None
    for item in market:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break
    if name_ == None:
        return [False,1]
    cost = price*amount
    users = await get_bank_data()
    bal = await update_bank(user)
    if bal[0]<cost:
        return [False,2]
    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            obj = {"item":item_name , "amount" : amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name , "amount" : amount}
        users[str(user.id)]["bag"] = [obj]        
    with open(db,"w") as f:
        json.dump(users,f)
    await update_bank(user,cost*-1,"wallet")
    return [True,"Worked"]

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    embeddoerr = discord.Embed(title="Error!!", description="ERR: **Still on cooldown** Please retry this command in {:.2f}s".format(error.retry_after), color=colors.red)
    embeddoerr.set_footer(text=f"Command Error for {interaction.user.name} on {datetime.datetime.now()}")
    return await interaction.response.send_message(embed=embeddoerr, ephemeral=True)

# @bot.on_error
# async def on_command_error(ctx: commands.Context, error):
#     embedonerr = discord.Embed(title="Error!!", description="You do not have permission to run this command as **its only for Shreyas-ITB**", color=colors.red)
#     embedonerr.set_footer(text=f"Command Error for {ctx.author.name} on {datetime.datetime.now()}")
#     return await ctx.send(embed=embedonerr)

@bot.tree.command(name="ping", description="Returns latency of the bot!")
@app_commands.guild_only()
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! Latency: {round(bot.latency * 1000)}ms", ephemeral=True)

@bot.tree.command(name="botinfo", description="Returns the information about the bot (main intention of the bot)")
@app_commands.guild_only()
async def botinfo(interaction: discord.Interaction):
    embed = discord.Embed(title="What does this bot do?", description="""
    This is a multipurpose bot which helps moderators guide new users in the community. It mainly helps them by giving a command which has all the info of what that user needs,  this saves the time of moderators typing or searching the appropriate links and long messages. In addition to this the bot has a very good economy system which keeps the users engaging and play with the bot more.. By playing with the bot users can earn something called as bot coins (not to be confused with bitcoins), bot coins are basically like in-game currency which you can trade/send the coins to other/with users. The botcoins after a certain limit you will be able to withdraw/exchange them to actual pkt coins..""", color=colors.gold)
    embed.add_field(name="Minimum requirements to exchange bot coins to pkt", value="""
    **You should** have your botcoin account created.
    **You should** have a 1000 bot coins in your bot coin account wallet before exchanging.""")
    embed.add_field(name="Exchange information", value="""
    As mentioned you should have a bot coin account and you should have 1000 coins in your account wallet. **1000 bot coins = 1 pkt coin**. And exchange command will be available once in 24 hours per user, means if you use the command you can't use it once again in the next 24 hours.""")
    embed.add_field(name="How to exchange?", value="You can refer ``/help`` for the command.")
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="botstatus", description="Returns the status and uptime of the bot")
@app_commands.guild_only()
async def botstatus(interaction: discord.Interaction):
    uptime = str(datetime.timedelta(seconds=int(round(time.time()-startTime))))
    embed = discord.Embed(title="Packetee Bot Status", description=f"The bot is up for {uptime}", color=colors.dark_magenta)
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="donate", description="Lets you donate some pkt for bot's faucet account")
@app_commands.guild_only()
async def donate(interaction: discord.Interaction):
    embed = discord.Embed(title="Packetee discord bot wallet address", description="""
    If you want to donate or contribute some Pkt to the bot's account then here is the address: 
    ```ini
    [ pkt1qj2d4hhgs5jvul59g2ews87gxtztpqz0es7rzuv ]```""", color=colors.blue)
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="donatetodev", description="Lets you donate some pkt for bot's faucet account")
@app_commands.guild_only()
async def donatetodev(interaction: discord.Interaction):
    embed = discord.Embed(title="Packetee developer wallet address", description="If you want to donate to Shreyas-ITB", color=colors.purple)
    embed.add_field(name="Bitcoin Address", value="""
    ```bc1q27hppwfte08fs7yu9w9mztl5hm3qz4tx8ne3d4```""")
    embed.add_field(name="Pkt Address", value="""
    ```ini
    [ pkt1qfnky5fssdl8evsk0t8kxupetaerm5c28wzxywx ]```""")
    embed.add_field(name="VerusCoin Address", value="""
    ```RMfrbs9eApM4VXV6htayiw1ks5WUGDvGtB```""")
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="stats", description="Returns the network stats of the coin")
@app_commands.guild_only()
async def stats(interaction: discord.Interaction):
    await interaction.response.defer()
    (encrypersec, bitspersec) = getstats()
    (minedtodate, reward) = getcoinstats()
    (anndiff, blkdiff) = getdiffstats()
    embed = discord.Embed(title="Network Stats", color=colors.magenta)
    embed.add_field(name="Network Bandwidth", value=humanbytes(bitspersec))
    embed.add_field(name="Encryptions per second", value=encrypersec)
    embed.add_field(name="Pkt Mined to date", value=f"{minedtodate} Pkt(s)")
    embed.add_field(name="Block Reward", value=f"{reward} Pkt(s)")
    embed.add_field(name="Current Block difficulty", value=blkdiff)
    embed.add_field(name="Announcent mining difficulty", value=anndiff)
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="poolinfo", description="Provides you the number of different pools for mining and says if its online/offline")
@app_commands.guild_only()
async def poolinfo(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="Pool Information", description="""
    Pool helps you mine coins very quickly compared to solo mining as you are mining with other people the higher the hashrate the higher rewards you get.
    Some of the pools that are available for mining pkt are as follows:
    **The Pkteer pool** ``http://pool.pkteer.com`` from Pkteer.
    **The PktPool** ``https://pool.pktpool.io`` from the official Pkt team.
    **The PktWorld pool** ``http://pool.pkt.world`` from ivo.
    **The Zetahash pool** ``https://stratum.zetahash.com`` from Srizbi.""", color=colors.green)
    try:
        pkteer = pythonping.ping("pool.pkteer.com")
        embed.add_field(name="Pkteer Pool Status", value=f":green_circle: This pool is online and working ({pkteer.rtt_avg_ms}ms).")
    except:
        embed.add_field(name="Pkteer Pool Status", value=":red_circle: This pool is offline unfortunately.")
    try:
        pktpool = pythonping.ping("pool.pktpool.io")
        embed.add_field(name="PktPool Status", value=f":green_circle: This pool is online and working ({pktpool.rtt_avg_ms}ms).")
    except:
        embed.add_field(name="PktPool Status", value=":red_circle: This pool is offline unfortunately.")
    try:
        pktworld = pythonping.ping("pool.pkt.world")
        embed.add_field(name="PktWorld Pool Status", value=f":green_circle: This pool is online and working ({pktworld.rtt_avg_ms}ms).")
    except:
        embed.add_field(name="PktWorld Pool Status", value=":red_circle: This pool is offline unfortunately.")
    try:
        ZetaHash = pythonping.ping("stratum.zetahash.com")
        embed.add_field(name="ZetaHash Pool Status", value=f":green_circle: This pool is online and working ({ZetaHash.rtt_avg_ms}ms).")
    except:
        embed.add_field(name="ZetaHash Pool Status", value=":red_circle: This pool is offline unfortunately.")
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="mininginfo", description="Provides you some info and docs page regarding how to mine")
@app_commands.guild_only()
async def mininginfo(interaction: discord.Interaction):
    embed = discord.Embed(title="Mining Information", description="""
    PacketCrypt is a bandwidth hard proof of work, this means it requires lots of bandwidth to mine. Miners collaborate with one another by sending small messages (called Announcements) and the sending of these messages requires a large amount of bandwidth. Miners who are working in collaboration with one another are members of a mining pool, therefore all mining of PacketCrypt is done in pools.
    **More Details on:** https://docs.pkt.cash/en/latest/mining/""", color=colors.dark_blue)
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="walletsetup", description="Provides you some info and docs page regarding how to setup wallet")
@app_commands.guild_only()
async def walletsetup(interaction: discord.Interaction):
    embed = discord.Embed(title="Wallet Setup Steps", description="""
    There are 6 types of wallets that you can use to store Pkt. 3 being mining wallets meaning that they are supported for mining and 3 being general pkt storable wallet. The general wallets and the mining wallets can be downloaded
    **from here:** https://pkt.cash/wallet/ and the CLI wallet can be setup from this document page **right here:** https://docs.pkt.cash/en/latest/pktd/pktwallet/""", color=colors.purple)
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="electrumimport", description="Gives you some steps on how to import your existing electrum wallet to Pkt wallet")
@app_commands.guild_only()
async def electrumimport(interaction: discord.Interaction):
    embed = discord.Embed(title="Electrum Import Steps", description="""Migrating from Electrum to PKTWallet If you have an electrum based wallet which becomes overloaded from too many transactions (e.g. from mining directly into it), then you will need to migrate your keys to a pktwallet instance. **Detailed info:** https://docs.pkt.cash/en/latest/pktd/migrating_from_electrum/""", color=colors.dark_teal)
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="pktelectrum", description="Provides you some details regarding the installation and setup of pkt electrum wallet")
@app_commands.guild_only()
async def pktelectrum(interaction: discord.Interaction):
    embed = discord.Embed(title="Pkt Electrum Steps", description="""Electrum is a good lightweight wallet for making and receiving payments, but it lacks scalability and is not appropriate for mining. How ever if you still wish to set it up then **Follow this guide:** https://docs.pkt.cash/en/latest/electrum/""", color=colors.dark_green)
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="wpkt", description="Provides you some details on wpkt and converting your pkt to wrapped pkt")
@app_commands.guild_only()
async def wpkt(interaction: discord.Interaction):
    embed = discord.Embed(title="Wpkt Steps", description=""" Wpkt is a wrapper around the wep-0044 and wep-0044-v1. It provides a way to convert your pkt to a wrapped pkt. You can find the steps to convert your Pkt into wrapped Pkt **Here:** https://docs.pkt.cash/en/latest/wrapped_pkt/""", color=colors.dark_magenta)
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="poolhost", description="Provides you the info on hosting pools and setting it up")
@app_commands.guild_only()
async def poolhost(interaction: discord.Interaction):
    embed = discord.Embed(title="Host your own pool", description="""You can host your own pkt pool with a powerful cloud server. You can follow **this documents page:** https://docs.pkt.cash/en/latest/mining/pool_setup_guide/""", color=colors.blue)
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="pktd", description="Provides you some info and documentation about pkt mainnet/node")
@app_commands.guild_only()
async def pktd(interaction: discord.Interaction):
    embed = discord.Embed(title="Pkt Daemon", description="""Pktd is the PKT full node blockchain software. It is a fork of btcd, the golang bitcoin instance. If you would like to run the full node on your server or cloud computer, you can refer **this link:** https://docs.pkt.cash/en/latest/pktd/""", color=colors.dark_orange)
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="balance", description="Returns the balance of the user")
@app_commands.guild_only()
async def balance(interaction: discord.Interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user
    await open_account(member)
    user = member
    users = await get_bank_data()
    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]
    em = discord.Embed(title=f"{member}'s Balance",color = colors.green)
    em.add_field(name="Wallet Balance", value=wallet_amt)
    em.add_field(name='Bank Balance',value=bank_amt)
    em.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed= em)

@bot.tree.command(name="daily", description="Gives you random amount of coins (Available once in 24 hours)")
@app_commands.guild_only()
@app_commands.checks.cooldown(1, 86400, key=lambda i: (i.user.id))
async def daily(interaction: discord.Interaction):
    await open_account(interaction.user)
    user = interaction.user
    users = await get_bank_data()
    earnings = random.randrange(50)
    embb = discord.Embed(title="Daily Dose of BotCoins", description=f"{interaction.user.mention} Got {earnings} coins!!", color=colors.green)
    embb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embb)
    users[str(user.id)]["wallet"] += earnings
    with open(db,'w') as f:
        json.dump(users,f)

@bot.tree.command(name="weekly", description="Gives you random amount of coins (Available once in 7 days)")
@app_commands.guild_only()
@app_commands.checks.cooldown(1, 604800, key=lambda i: (i.user.id))
async def weekly(interaction: discord.Interaction):
    await open_account(interaction.user)
    user = interaction.user
    users = await get_bank_data()
    earnings = random.randrange(120)
    embb = discord.Embed(title="Weekly Dose of BotCoins", description=f"{interaction.user.mention} Got {earnings} coins!!", color=colors.green)
    embb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embb)
    users[str(user.id)]["wallet"] += earnings
    with open(db,'w') as f:
        json.dump(users,f)

@bot.tree.command(name="monthly", description="Gives you random amount of coins (Available once in 30 days)")
@app_commands.guild_only()
@app_commands.checks.cooldown(1, 2592000, key=lambda i: (i.user.id))
async def monthly(interaction: discord.Interaction):
    await open_account(interaction.user)
    user = interaction.user
    users = await get_bank_data()
    earnings = random.randrange(160)
    embb = discord.Embed(title="Monthly Dose of BotCoins", description=f"{interaction.user.mention} Got {earnings} coins!!", color=colors.green)
    embb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embb)
    users[str(user.id)]["wallet"] += earnings
    with open(db,'w') as f:
        json.dump(users,f)

@bot.tree.command(name="withdraw", description="Lets you withdraw your botcoins from your bank to your wallet")
@app_commands.guild_only()
@app_commands.describe(amount = "amount of coins")
async def withdraw(interaction: discord.Interaction,amount: int):
    await open_account(interaction.user)
    if amount == None:
        em = discord.Embed(title="Error!!", description="Please enter the amount", color=colors.red)
        em.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=em, ephemeral=True)
        return
    bal = await update_bank(interaction.user)
    amount = int(amount)
    if amount > bal[1]:
        emb = discord.Embed(title="Error!!", description="You do not have sufficient balance", color=colors.red)
        emb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    if amount < 0:
        embb = discord.Embed(title="Error!!", description="Amount must be positive!", color=colors.red)
        embb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=embb, ephemeral=True)
        return
    await update_bank(interaction.user,amount)
    await update_bank(interaction.user,-1*amount,'bank')
    embo = discord.Embed(title="Packetee Withdraw", description=f"{interaction.user.mention} You withdrew {amount} coins", color=colors.green)
    embo.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embo)

@bot.tree.command(name="deposit", description="Lets you deposit your botcoins from your wallet to the bank")
@app_commands.guild_only()
@app_commands.describe(amount = "amount of coins")
async def deposit(interaction: discord.Interaction, amount: int):
    await open_account(interaction.user)
    if amount == None:
        em = discord.Embed(title="Error!!", description="Please enter the amount", color=colors.red)
        em.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=em, ephemeral=True)
        return
    bal = await update_bank(interaction.user)
    amount = int(amount)
    if amount > bal[1]:
        emb = discord.Embed(title="Error!!", description="You do not have sufficient balance", color=colors.red)
        emb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    if amount < 0:
        embb = discord.Embed(title="Error!!", description="Amount must be positive!", color=colors.red)
        embb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=embb, ephemeral=True)
        return
    await update_bank(interaction.user ,-1*amount)
    await update_bank(interaction.user ,amount,'bank')
    embo = discord.Embed(title="Packetee Deposit", description=f"{interaction.user.mention} You deposited {amount} coins", color=colors.green)
    embo.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embo)

@bot.tree.command(name="give", description="Lets you give your bot coins to which ever person you want")
@app_commands.guild_only()
@app_commands.describe(member = "mention member", amount = "amount of coins")
async def give(interaction: discord.Interaction, member : discord.Member, amount: int):
    await open_account(interaction.user)
    await open_account(member)
    if amount == None:
        em = discord.Embed(title="Error!!", description="Please enter the amount", color=colors.red)
        em.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=em, ephemeral=True)
        return
    bal = await update_bank(interaction.user)
    if amount == 'all':
        amount = bal[0]
    amount = int(amount)
    if amount > bal[0]:
        emb = discord.Embed(title="Error!!", description="You do not have sufficient balance", color=colors.red)
        emb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    if amount < 0:
        embb = discord.Embed(title="Error!!", description="Amount must be positive!", color=colors.red)
        embb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=embb, ephemeral=True)
        return
    wa = await get_bank_data()
    if wa[str(interaction.user.id)]["bank"] == 0 or wa[str(interaction.user.id)]["bank"] < amount:
        embob = discord.Embed(title="Error!!", description="You dont have enough money in your bank! deposit first..", color=colors.red)
        embob.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=embob, ephemeral=True)
        return
    else:
        await update_bank(interaction.user, -1*amount, 'bank')
    await update_bank(member,amount,'bank')
    embb = discord.Embed(title="Packetee Give", description=f"{interaction.user.mention} You gave {member} {amount} coins", color=colors.green)
    embb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embb)

@bot.tree.command(name="rob", description="Bring the richest users down by robbing them")
@app_commands.guild_only()
async def rob(interaction: discord.Interaction, member : discord.Member):
    await open_account(interaction.user)
    await open_account(member)
    bal = await update_bank(member)
    if bal[0]<100:
        embob = discord.Embed(title="Hmmm :(", description="Its useless to rob him.. He doesnt have anything.", color=colors.gold)
        embob.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=embob, ephemeral=True)
        return
    earning = random.randrange(0,bal[0])
    await update_bank(interaction.user ,earning)
    await update_bank(member,-1*earning)
    embb = discord.Embed(title="Packetee Rob", description=f"{interaction.user.mention} You robbed {member} and got {earning} coins", color=colors.green)
    embb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embb)

@bot.tree.command(name="market", description="Market where all items are listed")
@app_commands.guild_only()
async def markett(interaction: discord.Interaction):
    em = discord.Embed(title = "Packetee's Market", color=discord.Color.random())
    for item in market:
        name = item["name"]
        price = item["price"]
        desc = item["description"]
        em.add_field(name = name, value = f"${price} | {desc}")
        em.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed = em)

@bot.tree.command(name="buy", description="Lets you buy items from the market using your bot coins")
@app_commands.guild_only()
@app_commands.describe(item = "Item name", amount = "amount of items")
async def buy(interaction: discord.Interaction, item: str, amount: int = 1):
    await open_account(interaction.user)
    res = await buy_this(interaction.user, item, amount)
    if not res[0]:
        if res[1]==1:
            em = discord.Embed(title="Error!!", description="That Object isn't there!", color=colors.red)
            em.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return
        if res[1]==2:
            emb = discord.Embed(title="Error!!", description=f"You don't have enough money in your wallet to buy {amount} {item}", color=colors.red)
            emb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
    embd = discord.Embed(title="Error!!", description=f"You just bought {amount} {item}", color=colors.green)
    embd.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embd, ephemeral=True)

@bot.tree.command(name="inventory", description="Shows what all items are present in your inventory")
@app_commands.guild_only()
async def inventory(interaction: discord.Interaction):
    await open_account(interaction.user)
    user = interaction.user
    users = await get_bank_data()
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    em = discord.Embed(title = f"{interaction.user.name}'s Inventory", color=discord.Color.random())
    for item in bag:
        name = item["item"]
        amount = item["amount"]
        em.add_field(name = name, value = amount)    
        em.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed = em)
    
@bot.tree.command(name="sell", description="Sells the item from your inventory to the market")
@app_commands.guild_only()
@app_commands.describe(item = "Item name", amount = "amount of items")
async def sell(interaction: discord.Interaction, item: str, amount: int = 1):
    await open_account(interaction.user)
    res = await sell_this(interaction.user, item, amount)
    if not res[0]:
        if res[1]==1:
            em = discord.Embed(title="Error!!", description="That Object isn't there!", color=colors.red)
            em.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return
        if res[1]==2:
            emb = discord.Embed(title="Error!!", description=f"You don't have {amount} {item} in your inventory.", color=colors.red)
            emb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        if res[1]==3:
            embb = discord.Embed(title="Error!!", description=f"You don't have {item} in your inventory.", color=colors.red)
            embb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
            await interaction.response.send_message(embed=embb, ephemeral=True)
            return
    embbe = discord.Embed(title="Packetee Selling Market", description=f"You just sold {amount} {item}.", color=colors.green)
    embbe.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embbe)

@bot.command()
@commands.guild_only()
@commands.is_owner()
async def shutdown(ctx: commands.Context):
    em = discord.Embed(title="Packetee's Status", description="Shutting down the bot.. Saving DB changes and closing down the music node.", color=discord.Color.random())
    await ctx.send(embed=em)
    sleep(5)
    sys.exit()

@bot.command()
@commands.guild_only()
async def play(ctx: commands.Context, *, search: wavelink.YouTubeTrack):
    vc = ctx.voice_client
    if not vc:
        try:
            custom_player = wavelink.Player()
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=custom_player)
        except Exception:
            embe = discord.Embed(title="Error!!", description=f"Please join any VC channels and then try again..", color=colors.red)
            embe.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
            return await ctx.send(embed=embe, ephemeral=True)
    if vc.is_playing():
        vc.queue.put(item=search)
        em = discord.Embed(title="Packetee Music", description=f"The song ``{search.title}`` of artist **{search.author}** is now added to queue.", color=colors.green)
        em.set_thumbnail(url=search.thumbnail)
        em.add_field(name="Duration", value=converttime(search.duration))
        em.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        await ctx.send(embed=em)
    else:
        await vc.play(search)
        em = discord.Embed(title="Packetee Music", description=f"The song ``{vc.source.title}`` is now playing in **{vc.channel}**.", color=colors.green)
        em.set_thumbnail(url=search.thumbnail)
        em.add_field(name="Duration", value=converttime(vc.track.duration))
        em.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        await ctx.send(embed=em)

@bot.command()
@commands.guild_only()
async def pause(ctx: commands.Context):
    if not ctx.voice_client:
        emb = discord.Embed(title="Error!!", description="You are not playing any music in the VC.. Nothing to pause.", color=colors.red)
        emb.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=emb, ephemeral=True)
    elif not ctx.author.voice:
        embe = discord.Embed(title="Error!!", description="Please join the VC and then try the command again..", color=colors.red)
        embe.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=embe, ephemeral=True)
    else:
        vc: wavelink.Player = ctx.voice_client
    await vc.pause()
    em = discord.Embed(title="Packetee Music", description=f"The song ``{vc.source.title}`` playing in {vc.channel} has been paused.", color=colors.green)
    em.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
    await ctx.send(embed=em)

@bot.command()
@commands.guild_only()
async def resume(ctx: commands.Context):
    if not ctx.voice_client:
        emb = discord.Embed(title="Error!!", description="You are not playing any music in the VC.. Nothing to resume.", color=colors.red)
        emb.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=emb, ephemeral=True)
    elif not ctx.author.voice:
        embe = discord.Embed(title="Error!!", description="Please join the VC and then try the command again..", color=colors.red)
        embe.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=embe, ephemeral=True)
    else:
        vc: wavelink.Player = ctx.voice_client
    await vc.resume()
    em = discord.Embed(title="Packetee Music", description=f"The song ``{vc.source.title}`` playing in {vc.channel} has been resumed.", color=colors.green)
    em.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
    await ctx.send(embed=em)

@bot.command()
@commands.guild_only()
async def stop(ctx: commands.Context):
    if not ctx.voice_client:
        emb = discord.Embed(title="Error!!", description="You are not playing any music in the VC.. Nothing to stop.", color=colors.red)
        emb.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=emb, ephemeral=True)
    elif not ctx.author.voice:
        embe = discord.Embed(title="Error!!", description="Please join the VC and then try the command again..", color=colors.red)
        embe.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=embe, ephemeral=True)
    else:
        vc: wavelink.Player = ctx.voice_client
    await vc.stop()
    em = discord.Embed(title="Packetee Music", description=f"The song playing in {vc.channel} has been stopped.", color=colors.green)
    em.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
    await ctx.send(embed=em)

@bot.command()
@commands.guild_only()
async def disconnect(ctx: commands.Context):
    if not ctx.voice_client:
        emb = discord.Embed(title="Error!!", description="I am not in any voice channels.. Nothing to disconnect.", color=colors.red)
        emb.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=emb, ephemeral=True)
    elif not ctx.author.voice:
        embe = discord.Embed(title="Error!!", description="Please join the VC and then try the command again..", color=colors.red)
        embe.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=embe, ephemeral=True)
    else:
        vc: wavelink.Player = ctx.voice_client
    await vc.disconnect()
    em = discord.Embed(title="Packetee Music", description=f"Disconnected from {vc.channel} VC", color=colors.green)
    em.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
    await ctx.send(embed=em)

@bot.command()
@commands.guild_only()
async def queue(ctx: commands.Context):
    if not ctx.voice_client:
        emb = discord.Embed(title="Error!!", description="Im not in any Voice channels.. Can't show the queues right now.", color=colors.red)
        emb.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=emb, ephemeral=True)
    elif not ctx.author.voice:
        embe = discord.Embed(title="Error!!", description="Please join the VC and then try the command again..", color=colors.red)
        embe.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=embe, ephemeral=True)
    else:
        vc: wavelink.Player = ctx.voice_client
    if vc.queue.is_empty:
        embe = discord.Embed(title="Error!!", description="Your queue is empty..", color=colors.red)
        return await ctx.send(embed=embe, ephemeral=True)
    em = discord.Embed(title=f"{ctx.author.name}'s Song Queue", color=colors.green)
    queue = vc.queue.copy()
    song_count = 0
    for song in queue:
        song_count += 1
        em.add_field(name=f"Number of Songs: {song_count}", value=f"``{song.title}``")
        em.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
    await ctx.send(embed=em)

@bot.command()
@commands.guild_only()
async def volume(ctx: commands.Context, volume: int):
    if not ctx.voice_client:
        emb = discord.Embed(title="Error!!", description="You are not playing any song.. Nothing to increase or decrease.", color=colors.red)
        emb.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=emb, ephemeral=True)
    elif not ctx.author.voice:
        embe = discord.Embed(title="Error!!", description="Please join the VC and then try the command again..", color=colors.red)
        embe.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=embe, ephemeral=True)
    else:
        vc: wavelink.Player = ctx.voice_client
    if volume > 100:
        embedd = discord.Embed(title="Error!!", description="Volumes above ``100`` are not allowed..", color=colors.red)
        embedd.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=embedd, ephemeral=True)
    elif volume < 0:
        embeddd = discord.Embed(title="Error!!", description="Volumes below ``0`` are not allowed..", color=colors.red)
        embeddd.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=embeddd, ephemeral=True)
    em = discord.Embed(title="Packetee Music", description=f"The song ``{vc.source.title}`` playing in {vc.channel} has been set to ``{volume}``%", color=colors.green)
    em.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
    await ctx.send(embed=em)
    return await vc.set_volume(volume)

@bot.command()
@commands.guild_only()
async def nowplaying(ctx: commands.Context):
    if not ctx.voice_client:
        emb = discord.Embed(title="Error!!", description="You are not playing any song.. Nothing to see..", color=colors.red)
        emb.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=emb, ephemeral=True)
    elif not ctx.author.voice:
        embe = discord.Embed(title="Error!!", description="Please join the VC and then try the command again..", color=colors.red)
        embe.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=embe, ephemeral=True)
    else:
        vc: wavelink.Player = ctx.voice_client
    if not vc.is_playing:
        embe = discord.Embed(title="Error!!", description="Nothing seems to be playing..", color=colors.red)
        embe.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
        return await ctx.send(embed=embe, ephemeral=True)
    em = discord.Embed(title=f"Now Playing ``{vc.track.title}``", description=f"Playing in {vc.channel}", color=colors.green)
    em.add_field(name="Duration", value=converttime(vc.track.duration))
    em.set_footer(text=f"Command invoked by {ctx.author.name} on {datetime.datetime.now()}")
    await ctx.send(embed=em)

@bot.tree.command(name="leaderboard", description="Shows you the richest PktBoi in the world of Packetee")
@app_commands.guild_only()
async def leaderboard(interaction: discord.Interaction, membercount: int = 1):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)
    total = sorted(total,reverse=True)    
    em = discord.Embed(title = f"Top {membercount} Richest People" , description = "This is decided on the basis of raw money in the bank and wallet",color = discord.Color.random())
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = bot.get_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
        if index == membercount:
            break
        else:
            index += 1
    await interaction.response.send_message(embed = em)

@bot.tree.command(name="exchange", description="Exchanges bot coins to pkt (and sends it)")
@app_commands.guild_only()
@app_commands.checks.cooldown(1, 259200, key=lambda i: (i.user.id))
@app_commands.describe(address = "Your pkt address")
async def exchange(interaction: discord.Interaction, address: str):
    user = interaction.user
    users = await get_bank_data()
    try:
        wallet_amt = users[str(user.id)]["wallet"]
    except KeyError:
        e = discord.Embed(title="Error!!", description="You do not have a bot coin account Please run ``/balance`` first and then try again..", color=colors.red)
        e.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=e, ephemeral=True)
        return
    if address == None:
        em = discord.Embed(title="Error!!", description="Please enter the address", color=colors.red)
        em.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=em, ephemeral=True)
        return
    if not address.startswith('pkt1'):
        emmm = discord.Embed(title="Error!!", description="Please enter a valid Pkt address", color=colors.red)
        emmm.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=emmm, ephemeral=True)
        return
    if wallet_amt < 1000:
        emmmb = discord.Embed(title="Error!!", description="You do not meet the minimum exchange requirement: Wallet amount less than 1000..", color=colors.red)
        emmmb.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=emmmb, ephemeral=True)
        return
    else:
        await exchangereq(interaction.user, address=address)
        await update_bank(interaction.user, -1*1000, 'wallet')
        emm = discord.Embed(title="Exchange Status", description="You are added to the exchange queue. Shreyas will verify your exchange request and hopefully you will get paid within **24 Hours** Your balance will be deducted now itself.. Thanks..", color=colors.green)
        emm.set_footer(text=f"Command invoked by {interaction.user} on {datetime.datetime.now()}")
        await interaction.response.send_message(embed=emm, ephemeral=True)
        return

@bot.tree.command(name="exchangequeue", description="Shows you all the Exchange applications that are pending..")
@app_commands.guild_only()
async def exchangequeue(interaction: discord.Interaction):
    if os.stat(exchdb).st_size == 0:
        emb = discord.Embed(title="Exchange Queue", description="If you dont see your exchange application here, then you are most probably paid.. Paid user's application will be removed from the list however if you have earned again and you applied the form again then your application should be present here.. If you didnt get paid and your application is missing then you are probably rejected.", color=colors.gold)
        emb.add_field(name="**This is in Debug mode**", value="It is quite empty here (no applications found)..")
        emb.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}") 
    else:
        users = await get_addrs()
        emb = discord.Embed(title="Exchange Queue", description="If you dont see your exchange application here, then you are most probably paid.. Paid user's application will be removed from the list however if you have earned again and you applied the form again then your application should be present here.. If you didnt get paid and your application is missing then you are probably rejected.", color=colors.green)
        emb.add_field(name="**This is in Debug mode**", value=f"``{users}``")
        emb.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=emb, ephemeral=True)

@bot.command()
@commands.guild_only()
@commands.is_owner()
async def deletedb(ctx: commands.Context):
    try:
        await del_addrs()
        await ctx.send("Deleted Applications from the database..")
    except Exception as e:
        await ctx.send(f"Failed to delete applications: {e}")

@bot.tree.command(name="reportissue", description="Reports the issue to Shreyas-ITB which helps to keep the bot out of bugs")
@app_commands.guild_only()
@app_commands.describe(issue_title = "issue/bug title", issue_description = "issue/bug description")
async def reportissue(interaction: discord.Interaction, issue_title: str, issue_description: str):
    url = 'https://api.github.com/repos/%s/%s/issues' % (REPO_OWNER, REPO_NAME)
    session = requests.Session()
    session.auth = (GITUSER, GITPASS)
    issue = {'title': issue_title,
             'body': issue_description,
            }
    r = session.post(url, json.dumps(issue))
    if r.status_code == 201:
        embed = discord.Embed(title="Issue creation status", description="Successfully created Issue {0:s}".format(issue_title), color=colors.green)
    else:
        embed = discord.Embed(title="Issue creation status", description=f"Could not create Issue {issue_title} Response: {r.content}", color=colors.red)
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="help", description="Returns information regarding the commands")
@app_commands.guild_only()
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Command Documentation", color=colors.blue)
    embed.add_field(name="Bot related commands", value="""
    ``/botinfo`` - Returns information about the bot (Main intention of the bot).
    ``/ping`` - Returns latency of the bot (Speed of the bot).
    ``/help`` - Returns this help message (Command documentation).
    ``/botstatus`` - Returns the status and uptime of the bot.
    ``/donate`` - Lets you donate some pkt for bot's faucet account.
    ``/donatetodev`` - Gives you the donation address of Shreyas-ITB.
    ``/reportissue <issue title> <issue description>`` - Reports the issue to Shreyas-ITB which helps to keep the bot out of bugs.""")
    embed.add_field(name="Pkt related commands", value="""
    ``/stats`` - Returns the network stats of the coin.
    ``/mininginfo`` - Provides you some info and docs page regarding how to mine.
    ``/walletsetup`` - Provides you some info and docs page regarding how to setup wallet.
    ``/electrumimport`` - Gives you some steps on how to import your existing electrum wallet to Pkt wallet.
    ``/pktelectrum`` - Provides you some details regarding the installation and setup of pkt electrum wallet.
    ``/wpkt`` - Provides you some details on wpkt and converting your pkt to wrapped pkt.
    ``/poolinfo`` - Provides you the number of different pools for mining and says if its online/offline.
    ``/poolhost`` - Provides you the info on hosting pools and setting it up.
    ``/pktd`` - Provides you some info and documentation about pkt mainnet/node.
    """)
    embed.add_field(name="Economy related commands", value="""
    ``/balance <member mention>`` - Returns the balance of the user.
    ``/give <mention person> <amount of coins>`` - Lets you give your bot coins to which ever person you want.
    ``/exchange <your pkt address>`` - Exchanges bot coins to pkt (and sends it) (**Available once in 3 days**).
    ``/exchangequeue`` - Shows you the name and address of the users whose payments are pending.
    ``/daily`` - Gives you random amount of coins (**Available once in 24 hours**).
    ``/weekly`` - Gives you random amount of coins (**Available once in 7 days**).
    ``/monthly`` - Gives you random amount of coins (**Available once in 30 days**).
    ``/rob <member>`` - Lets you rob some amount of mentioned person's balance.
    ``/hunt`` - Lets you hunt an animal that you can sell for coins! (**Available once in 5 minutes**).
    ``/fish`` - Lets you fish in a dirty pond so that you could get a tool and hunt (**Available once in 5 minutes**).""")
    embed.add_field(name="Marketplace related commands", value="""
    ``/buy <item name> <amount of item>`` - Lets you buy items from the market using your bot coins.
    ``/sell <item name> <amount of item>`` - Sells the item from your inventory to the market.
    ``/inventory`` - Shows what all items are present in your inventory.
    ``/market`` - Market where all items are listed.""")
    embed.add_field(name="Music related commands", value="""
    ``pkt play <song name>`` - Plays the song in any voice channel.
    ``pkt pause`` - Pauses the song playing in the voice channel.
    ``pkt resume`` - Resumes the song playing in the voice channel.
    ``pkt queue`` - Shows your queue list.
    ``pkt stop`` - Stops the playing song in the voice channel.
    ``pkt volume <number>`` - Sets the volume of the song.
    ``pkt nowplaying`` - Gives you the information about the current playing song.
    ``pkt disconnect`` - Disconnects from the voice channel.""")
    embed.add_field(name="Administrator commands **NOT FOR GENERAL PUBLIC USE**", value="""
    ``pkt shutdown`` - Shuts down the bot completely in case of emergency. [**Shreyas-ITB only**]
    ``pkt deletedb`` - Clears the payment history of the users. [**Shreyas-ITB only**]""")
    embed.set_footer(text=f"Command invoked by {interaction.user.name} on {datetime.datetime.now()}")
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
