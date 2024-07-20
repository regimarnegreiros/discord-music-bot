import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio

from config import token

## Configuração do bot:
permissions = discord.Intents.default()
permissions.message_content = True
permissions.members = True
permissions.voice_states = True
bot = commands.Bot(command_prefix="-", intents=permissions)

async def load_cogs():
    for arquivo in os.listdir('categories'):
        if arquivo.endswith('.py'):
            await bot.load_extension(f"categories.{arquivo[:-3]}")


## Comandos gerais:
@bot.command()
async def ping(ctx:commands.Context):
    await ctx.send("Pong 🏓")


## Ao ligar:
@bot.event
async def on_ready():
    await load_cogs()
    await bot.change_presence(
        status=discord.Status.do_not_disturb, 
        activity=discord.Activity(type=discord.ActivityType.watching, name="dogs")
    )
    print("Funcionando.")


async def main():
    await bot.start(token)

asyncio.run(main())