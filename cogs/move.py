import discord
from discord.ext import commands
from utils.queue_manager import queue_manager
from utils.send_embed import *

class Move(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(aliases=['mover'], description="Move uma música na fila de uma posição para outra.")
    async def move(self, ctx: commands.Context, from_index: int, to_index: int):
        queue = queue_manager.get_queue(ctx.guild.id)
        if from_index < 1 or from_index > len(queue) or to_index < 1 or to_index > len(queue):
            await send_simple_embed(
                ctx, "Índice inválido. Por favor, forneça índices válidos.",
                discord.Color.red()
            )
        else:
            title = queue_manager.move_track(ctx.guild.id, from_index, to_index)
            await send_simple_embed(
                ctx, f'Movido **{title}** da posição {from_index} para a posição {to_index}.',
                discord.Color.blue()
            )

async def setup(bot):
    await bot.add_cog(Move(bot))
