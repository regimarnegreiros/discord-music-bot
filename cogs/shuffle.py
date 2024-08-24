import discord
from discord.ext import commands
from utils.queue_manager import queue_manager
from utils.send_embed import *

class Shuffle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(aliases=['random' ,'embaralhar', 'aleatorizar'], description="Embaralha a fila.")
    async def shuffle(self, ctx: commands.Context):
        queue = queue_manager.get_queue(ctx.guild.id)
        if not queue:
            await send_simple_embed(
                ctx, "Não há músicas na fila para colocar no aleatório. Adicione algumas músicas primeiro!",
                discord.Color.red()
            )
        else:
            queue_manager.shuffle_queue(ctx.guild.id)
            await send_simple_embed(ctx, "A fila de músicas foi embaralhada!", discord.Color.blue())

async def setup(bot):
    await bot.add_cog(Shuffle(bot))