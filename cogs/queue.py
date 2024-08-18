import discord
from discord.ext import commands
from utils.is_url import *
from utils.queue_manager import queue_manager
from utils.send_embed import *

class Queue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(aliases=['fila'], description="Mostra a fila de músicas.")
    async def queue(self, ctx: commands.Context):
        queue = queue_manager.get_queue(ctx.guild.id)
        if not queue:
            await send_simple_embed(
                ctx, "A fila de músicas está vazia. Adicione algumas músicas para ver a lista!",
                discord.Color.blue()
            )
            return
        
        queue_list = '\n'.join([f'{idx+1}. {song_info["title"]}' for idx, song_info in enumerate(queue[:20])])
        remaining_songs = len(queue) - 20
        message_content = f'```{queue_list}```'
        if remaining_songs > 0:
            message_content += f'```\n...e mais {remaining_songs} músicas na fila.```'
        await ctx.send(message_content)

async def setup(bot):
    await bot.add_cog(Queue(bot))