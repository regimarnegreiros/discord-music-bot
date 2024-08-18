import discord
from discord.ext import commands
from utils.queue_manager import queue_manager
from utils.send_embed import *

class Remove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(aliases=['remover'], description="Remove uma música da fila pelo índice.")
    async def remove(self, ctx: commands.Context, index: int):
        queue = queue_manager.get_queue(ctx.guild.id)
        if index < 1 or index > len(queue):
            await send_simple_embed(
                ctx, "Índice inválido. Por favor, forneça um índice válido.",
                discord.Color.red()
            )
        else:
            removed_song = queue_manager.remove_from_queue(ctx.guild.id, index - 1)
            await send_simple_embed(ctx, f'Removido da fila: **{removed_song.get('title')}**', discord.Color.blue())

async def setup(bot):
    await bot.add_cog(Remove(bot))