import discord
from discord.ext import tasks, commands
import datetime as d
import requests
from bs4 import BeautifulSoup as bs
import re

TOKEN = ''

client = discord.Client()
time = d.datetime.now().strftime("%H:%M:%S")
print(time)

full_date = d.date.today()
string_date = str(full_date)

# format date into proper format
format_date = string_date[0:4] + '/' + string_date[5:7] +'/' + string_date[8:]
daily_devo_url = "https://odb.org/" + format_date
url = "https://api.experience.odb.org/devotionals/podcast/?country=TW"
r = requests.get(url)

soup = bs(r.content, 'lxml')
devotional = soup.find('description').text
# print(devotional)

TAG_RE = re.compile(r']]>')
content = TAG_RE.sub('', devotional)

target_channel = 'daily-devotion'
bot = commands.Bot("!")

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@bot.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)

    if message.author == client.user:
        return
    
    if message.channel.name == target_channel:
        if user_message.lower() == '!devo':
            await message.channel.send(format_date + " Our Daily Bread: " + daily_devo_url)
            await message.channel.send(content)
            return

@tasks.loop(hours=24)
async def called_once_a_day():
    message_channel = bot.get_channel()
    print(f"Got channel {message_channel}")
    await message_channel.send(format_date + " Our Daily Bread: " + daily_devo_url)
    await message_channel.send(content)

@called_once_a_day.before_loop
async def before():
    await bot.wait_until_ready()
    print("Finished waiting")

called_once_a_day.start()
bot.run(TOKEN)
