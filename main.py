import asyncio
import datetime
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

<<<<<<< HEAD
ROLE_IDS = [1435807108414177330,1435807199887753448] # [1372405122566459433, 1372455418319732926] # [Engineering, Usability]
USER_IDS = [593182696046329879] # Ramsey
ESCALATION_IDS = [180895908416847872] # [622934594609610752] # [Rohit]
CHANNEL_IDS = [826650354803408948] #[1372406245251747941] # [#builds]
=======
ROLE_IDS = [1372405122566459433, 1372455418319732926] # [Engineering, Usability]
ESCALATION_IDS = [622934594609610752] # [Rohit]
CHANNEL_IDS = [1372406245251747941] # [#builds]
>>>>>>> 9ed4a20 (moved files into the folder)

TZ = ZoneInfo("America/Los_Angeles")
REMINDER_DAY = 1     # Tuesday (Mon=0, Tue=1, etc)
REMINDER_HOUR = 16   # 0-23
REMINDER_MINUTE = 30 # 0-59

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(time=datetime.time(hour=REMINDER_HOUR, minute=REMINDER_MINUTE, tzinfo=TZ))
async def build_reminder():
    now = datetime.datetime.now(TZ)
    if now.weekday() != REMINDER_DAY:
        return

    print(f"[{datetime.datetime.now()}] Starting reminder")

    channel = bot.get_channel(CHANNEL_IDS[0])
    if not channel:
        print("Channel not found")
        return

    reminder_message = await channel.send(f'<@&{ROLE_IDS[1]}> - Can you confirm "✅ Build is in" by 5:00 PM PT?\n<@&{ROLE_IDS[0]}> reminder: upload by 5:00 PM PT.')
    await reminder_message.add_reaction("✅")

    print(f"[{datetime.datetime.now()}] Reminder sent in #{channel.name} (ID: {CHANNEL_IDS[0]})")

    def check(reaction, user):
        if user.bot:
            return False
        if reaction.message.id != reminder_message.id:
            return False
        if str(reaction.emoji) != "✅":
            return False

        member = reaction.message.guild.get_member(user.id)
        return any(role.id in ROLE_IDS for role in member.roles)

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=35*60.0, check=check) # 35 minutes
        await channel.send(f'✅ Confirmed by {user.name} at {datetime.datetime.now().strftime("%H:%M %p")}!')
        print(f"[{datetime.datetime.now()}] Confirmation received from {user} in #{channel.name}")

    except asyncio.TimeoutError:
        await channel.send(f' <@{ESCALATION_IDS[0]}> <@&{ROLE_IDS[0]}> <@&{ROLE_IDS[1]}> ⏰ No confirmation by 5:00 PM PT. Rohit: please verify with Engineering & Usability.')
        print(f"[{datetime.datetime.now()}] No confirmation, escalation triggered in #{channel.name}")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    if not build_reminder.is_running():
        build_reminder.start()

bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
