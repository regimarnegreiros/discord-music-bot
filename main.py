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
PREFIX = "-"
bot = commands.Bot(command_prefix=PREFIX, intents=permissions)

async def load_cogs():
    for arquivo in os.listdir('categories'):
        if arquivo.endswith('.py'):
            await bot.load_extension(f"categories.{arquivo[:-3]}")


## Comandos gerais:
@bot.hybrid_command(description="Responde o usuário com pong.")
async def ping(ctx: commands.Context):
    await ctx.send("Pong 🏓")

# Remover o comando de ajuda padrão:
bot.remove_command('help')

def create_command_field(bot, command_name, custom_title=None):
    command = bot.get_command(command_name)
    if not command:
        return None

    aliases = command.aliases
    description = command.description or "Nenhuma descrição fornecida."
    aliases_str = ", ".join([f"{PREFIX}{alias}" for alias in aliases])
    if custom_title:
        field_name = PREFIX + custom_title
    else:
        field_name = f"{PREFIX}{command.name}"
    
    if aliases:
        field_value = f"{description}\nComandos alternativos: {aliases_str}"
    else:
        field_value = description
    
    return {"name": field_name, "value": field_value, "inline": False}

@bot.hybrid_command(aliases=['ajuda', 'h'], description="Exibe os comandos existentes.")
async def help(ctx: commands.Context):
    embed = discord.Embed(
        title="Lista de Comandos",
        color=discord.Color.blue()
    )

    # Tópicos de comandos
    topics = {
        "🎵 Comandos de Música": [
            ('play', 'play [link/nome da música]'),
            ('skip', 'skip [quantidade (opcional)]')
        ],
        "🎶 Comandos de fila": [
            ('queue', None),
            ('remove', 'remove [index]'),
            ('move', 'move [do_index] [para_index]'),
            ('clear', None),
            ('random', None)
        ],
        "🔗 Comandos de Conexão": [
            ('join', None),
            ('exit', None)
        ]
    }

    for topic, commands_in_order in topics.items():
        embed.add_field(name="\u200b", value=f"**{topic}**", inline=False)
        for command_name, custom_title in commands_in_order:
            field = create_command_field(bot, command_name, custom_title)
            if field:
                embed.add_field(**field)

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