import discord
from discord.ext import commands
from utils.queue_manager import queue_manager
from utils.play_next import play_next
from utils.send_embed import *

class Join(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(aliases=['entrar', 'connect'], description="Entra no canal de voz.")
    async def join(self, ctx: commands.Context):
        if not ctx.author.voice:
            await send_simple_embed(ctx, "Você precisa estar em um canal de voz para usar este comando!", discord.Color.red())
            return

        channel = ctx.author.voice.channel
        message = None
        
        if ctx.voice_client:
            if ctx.voice_client.channel == channel:
                msg_text = "Já estou conectado a este canal de voz!"
            else:
                await ctx.voice_client.move_to(channel)
                msg_text = "Conectado ao canal de voz!"
        else:
            await channel.connect(timeout=30.0, reconnect=True)
            msg_text = "Conectado ao canal de voz!"
            
        if not ctx.voice_client.is_playing() and queue_manager.get_queue(ctx.guild.id):
            await play_next(ctx, self.bot, queue_manager) # Volta a tocar caso tenha músicas na fila

        if ctx.interaction:
            message = await send_simple_embed(ctx, msg_text, discord.Color.green())
            await message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('✅')

async def setup(bot):
    await bot.add_cog(Join(bot))