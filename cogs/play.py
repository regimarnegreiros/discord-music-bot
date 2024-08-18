import discord
from discord.ext import commands
from utils.connect_channel import connect_channel
from utils.is_url import *

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(aliases=['p'], description="Adiciona uma música à fila. Suporta links do YouTube, Spotify e pesquisas.")
    async def play(self, ctx: commands.Context, *, search):
        
        if is_spotify_url(search):
            spotify_command = self.bot.get_command('spotify')
            if spotify_command:
                await ctx.invoke(spotify_command, search=search)
            else:
                await ctx.send("Comando `spotify` não encontrado.")
            return
        
        try:
            youtube_command = self.bot.get_command('youtube')
            if youtube_command:
                await ctx.invoke(youtube_command, search=search)
            else:
                await ctx.send("Comando `youtube` não encontrado.")
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Play(bot))
