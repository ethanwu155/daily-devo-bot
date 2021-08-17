from typing import Text
import discord
from discord.ext import tasks, commands
import datetime as d
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time


TOKEN = ''

client = discord.Client()

target_channel = ''
bot = commands.Bot("!")

PATH = ''

def get_date():
    now = d.datetime.today()
    format_date= now.strftime("%Y/%m/%d")

    return format_date

def perform_scrap():
    driver = webdriver.Chrome(PATH)
    url = "https://odb.org/" + get_date()
    driver.get(url)
    time.sleep(10)
    content= bs(driver.page_source,"lxml")

    # Title
    title = content.find("h1",class_="devo-title").text
    title = '**' + title + '**'

    # Bible in a year
    bible_in_year = content.find("div",class_="biay-wrap").text
    
    # bible in year verse list
    in_year_verse = content.find("ul", class_='verse-list').text

    # Devo Verse
    devo_verse = content.find("div", class_="verseArea").text
    devo_verse = '_' + devo_verse + '_'

    # scripture insight
    insight = content.find("div", class_='devo-scriptureinsight').text

    # insights title
    insights_title = content.find("span", class_='scripture').text
    insights_title = '**' + insights_title + '**'

    # insights verse
    insights_verse = content.find("button", class_='skipRefTagger scripture btn large primary-light').text

    # Content
    article = content.find("article",class_="content").text

    # Reflect Title
    reflect_title = content.find("h4",class_="devo-prayer-heading").text
    reflect_title = '**' + reflect_title + '**'
    
    # Reflection
    reflection = content.find("div",class_="devo-reflection devo-question").text

    # Prayer
    prayer = content.find("div", class_="devo-reflection devo-prayer").text
    
    driver.close()

    return title, article, reflect_title, reflection, prayer, bible_in_year, devo_verse, insight, insights_title, insights_verse, in_year_verse


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username} : {user_message} {channel}')

    if message.author == client.user:
        return
    
    if message.channel.name == target_channel:
        if user_message.lower() == '!devo':
            devo_post = perform_scrap()

            await message.channel.send(devo_post[0] + '\n\n' + devo_post[5] + '\n\n' + devo_post[6] + '\n\n'
                                        + devo_post[7] + '\n\n' + devo_post[1] + '\n' + devo_post[2] + '\n\n' 
                                        + devo_post[3] + '\n\n' + devo_post[4])
            return

@tasks.loop(hours=24)
async def called_once_a_day():
    message_channel = bot.get_channel()
    print(f"Got channel {message_channel}")
    print('{0.user}'.format(bot) + ' posted daily devo')
    date = d.datetime.now().strftime("%B %d %Y")
    await message_channel.send(date + ' : ' + "https://odb.org/" + get_date() + '\n\n')
    devo_post = perform_scrap()
    await message_channel.send(devo_post[0] + '\n\n' + '**Bible in a Year:** ' + devo_post[10] + '\n\n' + devo_post[6] + '\n\n'
            + devo_post[8] + ' ' + devo_post[9] + '\n\n' + devo_post[1] + '\n' + devo_post[2] + '\n\n' 
            + devo_post[3] + '\n\n' + devo_post[4])


@called_once_a_day.before_loop
async def before():
    await bot.wait_until_ready()
    print("Finished waiting")

called_once_a_day.start()
bot.run(TOKEN)