import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
from dotenv import load_dotenv
from config import COLOR


## Configuração do bot:
load_dotenv()
TOKEN = os.getenv('TOKEN')
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
@bot.hybrid_command(description="Responde o usuário com pong.")
async def ping(ctx:commands.Context):
    await ctx.send("Pong 🏓")

# Remover o comando de ajuda padrão:
bot.remove_command('help')

@bot.hybrid_command(aliases=['ajuda', 'h'], description="Exibe os comandos exitentes.")
async def help(ctx:commands.Context):
    embed = discord.Embed(
        title="Comandos de Música",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="-play [link/nome da música]",
        value="Adiciona uma música à fila. Suporta links do YouTube e pesquisas.\nComando alternativo: -p",
        inline=False
    )
    embed.add_field(
        name="-skip",
        value="Pula para a próxima música na fila. \nComandos alternativos: -pular, -next",
        inline=False
    )
    embed.add_field(
        name="-queue",
        value="Mostra a fila de músicas.\nComando alternativo: -fila",
        inline=False
    )
    embed.add_field(
        name="-remove [index]",
        value="Remove uma música da fila pelo índice.\nComando alternativo: -remover",
        inline=False
    )
    embed.add_field(
        name="-clear",
        value="Limpa a fila de músicas.\nComandos alternativos: -limpar, -clear_queue",
        inline=False
    )
    embed.add_field(
        name="-random",
        value="Embaralha a fila de músicas.\nComandos alternativos: -embaralhar, -aleatorizar"
    )
    embed.add_field(
        name="-join",
        value="Faz o bot entrar no canal de voz.\nComandos alternativos: -entrar, -connect",
        inline=False
    )
    embed.add_field(
        name="-exit",
        value="Faz o bot sair do canal de voz.\nComandos alternativos: -sair, -disconnect",
        inline=False
    )

    await ctx.send(embed=embed)

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
    await bot.tree.sync()
    await bot.change_presence(
        status=discord.Status.do_not_disturb, 
        activity=discord.Activity(type=discord.ActivityType.listening, name="música")
    )
    print(f'Conectado como {bot.user} (ID: {bot.user.id})')


async def main():
    await bot.start(TOKEN)

asyncio.run(main())