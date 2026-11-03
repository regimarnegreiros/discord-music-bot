import discord
from discord.ext import commands
from utils.queue_manager import queue_manager
from utils.send_embed import *

class SkipTo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(aliases=['pularpara', 'jump'], description="Pula para uma música específica.")
    async def skipto(self, ctx: commands.Context, index: int):
        queue = queue_manager.get_queue(ctx.guild.id)

        if index < 1 or index > len(queue):
            await send_simple_embed(
                ctx, "Por favor, insira um número válido correspondente a uma música na fila.", 
                discord.Color.red()
            )
            return

        if ctx.voice_client and ctx.voice_client.is_playing():
            queue_manager.remove_slice_from_queue(ctx.guild.id, index - 1)
            queue = queue_manager.get_queue(ctx.guild.id)
            ctx.voice_client.stop()
            if ctx.interaction:
                await send_simple_embed(
                    ctx, f"Pulei para a música **{queue[0].get('title')}** na fila!", 
                    discord.Color.blue()
                )
            else:
                await ctx.message.add_reaction('⏭️')
        else:
            await send_simple_embed(ctx, "Não há música tocando no momento.", discord.Color.red())

async def setup(bot):
    await bot.add_cog(SkipTo(bot))
