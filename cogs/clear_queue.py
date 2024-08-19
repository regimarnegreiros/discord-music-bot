import discord
from discord.ext import commands
from utils.send_embed import *
from utils.queue_manager import queue_manager

class ClearQueue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(aliases=['clear', 'limpar'], description="Limpa a fila de músicas.")
    async def clear_queue(self, ctx: commands.Context):
        queue_manager.clear_queue(ctx.guild.id)
        await send_simple_embed(ctx, "A fila foi limpa!", discord.Color.blue())

async def setup(bot):
    await bot.add_cog(ClearQueue(bot))
