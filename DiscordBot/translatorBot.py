import discord
from discord.ext import commands
import googletrans
from googletrans import Translator
from datetime import datetime, date
from functools import reduce
from chatbot import Chat, register_call
import requests
import wikipedia
import json
import pickle
import ctx
import random
import asyncio
import os

#Globals
bot = commands.Bot(command_prefix='~')
bot.remove_command("help")


#Events

@bot.event
async def on_ready():
    activity = discord.Game(name="w/ py code. Coming soon in JS")
    await bot.change_presence(status=discord.Status.idle, activity = activity)

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    
    if not message.content.startswith('~'):
        return

    await bot.process_commands(message)

@register_call("whoIs")
def who_is(session, query):
    try:
        return wikipedia.summary(query)
    except Exception:
        for new_query in wikipedia.search(query):
            try:
                return wikipedia.summary(new_query)
            except Exception:
                pass
    return "I don't know about "+query

template_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
 "chatbotTemplate","chatbotTemplate.template")
chat=Chat(template_file_path)

#Commands

@bot.command(aliases=['Terminate'])
async def terminate(ctx):
    await ctx.send("Terminating...")
    await bot.logout()


@bot.group(invoke_without_command=True)
async def help(ctx):
    embed = discord.Embed(title ="Help", description = "Available bot commands",
     color = (0x2ecc71))
    embed.add_field(name = "add", value = "basic addition \n~add N N")
    embed.add_field(name = "tr", value = "translates to specified langauge \n~tr langauge Message")
    embed.add_field(name = "oracle", value = "statistical answers \n~oracle Message")
    embed.add_field(name = "klepto", value = "bot chat and wiki search \n~klepto Message")
    embed.add_field(name = "rl", value = "roll dice \n~rl NdN")

    await ctx.send(embed = embed)    



@bot.command()
async def add(ctx, left: int, right: int):
    result = left + right
    embed = discord.Embed(title ="Adding", description = result, color = (0x2ecc71))
    await ctx.send(embed = embed)


@bot.command(aliases=['tr'])
async def translate(ctx, lang_to, *args):
    lang_to = lang_to.lower()
    if lang_to not in googletrans.LANGUAGES and lang_to not in googletrans.LANGCODES:
        result = ("Invalid language to translate text to")
        embed = discord.Embed(title ="Translating Failed", description = result, color = (0x2ecc71))
        raise commands.BadArgument(embed = embed)

    text = ' '.join(args)
    translator = googletrans.Translator()
    text_translated = translator.translate(text, dest=lang_to).text
    embed = discord.Embed(title ="Translating", description = text_translated, color = (0x2ecc71))
    await ctx.send(embed = embed)


@bot.command(aliases=['rl'])
async def roll(ctx, dice: str):
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        result = ('Format has to be in NdN!')
        embed = discord.Embed(title ="Roll incomplete", description = result, color = (0x2ecc71))
        await ctx.send(embed = embed)
        return

    result = ','.join(str(random.randint(1, limit)) for r in range(rolls))
    embed = discord.Embed(title ="Roll results", description = result, color = (0x2ecc71))
    await ctx.send(embed = embed)


@bot.command(aliases=['pick'])
async def choose(ctx, *choices: str):
    result = random.choice(choices)
    embed = discord.Embed(title ="Picking", description = result, color = (0x2ecc71))
    await ctx.send(embed = embed)


@bot.command()
async def oracle(ctx, *args):
    query = '+'.join(args)
    url = "https://api.wolframalpha.com/v1/result?appid=KGK9LG-ALYPV5JG5L&i={}%3F".format(query)
    response = requests.get(url)
    result = response.text

    if response.status_code == 501:
        result = ("Unable to process that query")
        embed = discord.Embed(title ="Error", description = result, color = (0x2ecc71))
        await ctx.send(embed = embed)
        return
    embed = discord.Embed(title ="Here's what I know about that", description = result, color = (0x2ecc71))
    await ctx.send(embed = embed)

@bot.command(pass_context = True)
async def klepto(ctx,*,message):
    result = chat.respond(message)
    if(len(result)<=2048):
        embed=discord.Embed(title="Klepto", 
        description = result, color = (0x2ecc71))
        await ctx.send(embed=embed)
    else:
        embedList = []
        n=2048
        embedList = [result[i:i+n] for i in range(0, len(result), n)]
        for num, item in enumerate(embedList, start = 1):
            if(num == 1):
                embed = discord.Embed(title="Here's what wiki says about that...", 
                description = item, color = (0x2ecc71))
                embed.set_footer(text="Page {}".format(num))
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(description = item, color = (0x2ecc71))
                embed.set_footer(text = "Page {}".format(num))
                await ctx.send(embed = embed)

    
bot.run('insertTokenHere')