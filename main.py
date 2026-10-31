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
        activity=discord.Streaming(name=f"{PREFIX}help", url="https://www.youtube.com/watch?v=SECVGN4Bsgg")
    )
    print(f'Conectado como {bot.user} (ID: {bot.user.id})')


async def main():
    if not TOKEN:
        print("\n❌ ERRO: A variável TOKEN não foi encontrada no arquivo .env.")
        print("Configure seu token do Discord no arquivo .env e reinicie o container.\n")
        await asyncio.sleep(60)
        return

    try:
        async with bot:
            await bot.start(TOKEN)
    except discord.errors.LoginFailure:
        print("\n" + "=" * 65)
        print("❌ [ERRO DE AUTENTICAÇÃO] O TOKEN do Discord é inválido ou expirou!")
        print("A API do Discord rejeitou a conexão com erro 401: Unauthorized.")
        print("\nPara corrigir:")
        print(" 1. Acesse https://discord.com/developers/applications")
        print(" 2. Selecione sua aplicação -> menu 'Bot' -> clique em 'Reset Token'")
        print(" 3. Copie o novo token e cole no arquivo .env:")
        print("    TOKEN=seu_novo_token_aqui")
        print(" 4. Reinicie o container com: docker compose restart")
        print("=" * 65 + "\n")
        await asyncio.sleep(60)
    except Exception as e:
        print(f"\n❌ [ERRO INESPERADO AO INICIAR O BOT]: {e}\n")
        await asyncio.sleep(60)

asyncio.run(main())