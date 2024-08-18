import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
from dotenv import load_dotenv
from config.settings import PREFIX


## Configuração do bot:
load_dotenv()
TOKEN = os.getenv('TOKEN')
permissions = discord.Intents.default()
permissions.message_content = True
permissions.members = True
permissions.voice_states = True
bot = commands.Bot(command_prefix=PREFIX, intents=permissions)

async def load_cogs():
    for arquivo in os.listdir('cogs'):
        if arquivo.endswith('.py'):
            try:
                await bot.load_extension(f"cogs.{arquivo[:-3]}")
            except Exception as e:
                print(f'Erro ao carregar cog {arquivo}: {e}')


## Comandos gerais:
@bot.hybrid_command(description="Responde o usuário com pong.")
async def ping(ctx: commands.Context):
    await ctx.send("Pong 🏓")


## Ao ligar:
@bot.event
async def on_ready():
    await load_cogs()
    await bot.tree.sync()
    await bot.change_presence(
        status=discord.Status.do_not_disturb, 
        activity=discord.Activity(type=discord.ActivityType.listening, name=f"{PREFIX}help")
    )
    print(f'Conectado como {bot.user} (ID: {bot.user.id})')


async def main():
    async with bot:
        await bot.start(TOKEN)

asyncio.run(main())