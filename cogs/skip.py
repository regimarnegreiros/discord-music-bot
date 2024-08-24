import discord
from discord.ext import commands
from utils.queue_manager import queue_manager
from utils.send_embed import *

class Skip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(aliases=['pular', 'next'], description="Pula para a próxima música.")
    async def skip(self, ctx: commands.Context):
        queue = queue_manager.get_queue(ctx.guild.id)
        
        if ctx.voice_client and ctx.voice_client.is_playing():
            if queue:
                ctx.voice_client.stop()
                if ctx.interaction:
                    await send_simple_embed(ctx, "Pulando para a próxima música!", discord.Color.blue())
                else:
                    await ctx.message.add_reaction('⏭️')
            else:
                ctx.voice_client.stop()
                if ctx.interaction:
                    await send_simple_embed(ctx, "Não há músicas na fila para pular.", discord.Color.red())
                else:
                    await ctx.message.add_reaction('⏭️')


async def setup(bot):
    await bot.add_cog(Skip(bot))
