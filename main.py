import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio

from BOT_TOKEN import token
from config import COLOR

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

@bot.event
async def on_voice_state_update(member, before, after):
    # Verificar se o usuário entrou em um canal de voz
    if before.channel is None and after.channel is not None:
        channel_name = after.channel.name
        print(f'{COLOR["BOLD_WHITE"]}{member.display_name}{COLOR["RESET"]} entrou: {COLOR["BOLD_WHITE"]}{channel_name}{COLOR["RESET"]}')

    # Verificar se o usuário saiu de um canal de voz
    elif before.channel is not None and after.channel is None:
        channel_name = before.channel.name
        print(f'{COLOR["BOLD_WHITE"]}{member.display_name}{COLOR["RESET"]} saiu: {COLOR["BOLD_WHITE"]}{channel_name}{COLOR["RESET"]}')

    # Verificar se o usuário mudou de canal de voz
    elif before.channel is not None and after.channel is not None and before.channel != after.channel:
        old_channel_name = before.channel.name
        new_channel_name = after.channel.name
        print(f'{COLOR["BOLD_WHITE"]}{member.display_name}{COLOR["RESET"]} trocou: {COLOR["BOLD_WHITE"]}{old_channel_name}{COLOR["RESET"]} para {COLOR["BOLD_WHITE"]}{new_channel_name}{COLOR["RESET"]}')


## Ao ligar:
@bot.event
async def on_ready():
    await load_cogs()
    await bot.change_presence(
        status=discord.Status.do_not_disturb, 
        activity=discord.Activity(type=discord.ActivityType.watching, name="dogs")
    )
    print(f'Conectado como {bot.user} (ID: {bot.user.id})')


async def main():
    await bot.start(token)

asyncio.run(main())