import discord
from discord.ext import commands
from utils.send_embed import *

class Exit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(aliases=['sair', 'disconnect'], description="Sai do canal de voz.")
    async def exit(self, ctx: commands.Context):
        voice_client = ctx.guild.voice_client

        if not voice_client:
            await send_simple_embed(ctx, "O bot não está atualmente em um canal de voz!", discord.Color.red())
            return

        if voice_client.is_playing():
            voice_client.stop()
        
        await voice_client.disconnect()

        if ctx.interaction:
            message = await send_simple_embed(ctx, "Saindo do canal de voz!", discord.Color.green())
            await message.add_reaction('👋')
        else:
            await ctx.message.add_reaction('👋')

async def setup(bot):
    await bot.add_cog(Exit(bot))
