import discord
from discord.ext import commands
from utils.queue_manager import queue_manager
from utils.send_embed import *
from utils.play_next import set_send_queue_finish_msg

class Stop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(aliases=['parar'], description="Para de tocar e limpa a fila de músicas")
    async def stop(self, ctx: commands.Context):
        global send_queue_finish_msg

        if not ctx.interaction:
            await ctx.message.add_reaction('🛑')

        if ctx.voice_client and ctx.voice_client.is_playing():
            queue_manager.clear_queue(ctx.guild.id)
            ctx.voice_client.stop()
            set_send_queue_finish_msg(False)
            if ctx.interaction:
                await send_simple_embed(ctx, "Parando de tocar!", discord.Color.blue())
        else:
            if ctx.interaction:
                await send_simple_embed(ctx, "O bot não está tocando nada.", discord.Color.red())


async def setup(bot):
    await bot.add_cog(Stop(bot))
