from discord.ext import commands
from utils.queue_manager import queue_manager
import asyncio
from utils.play_next import previous_now_playing_msgs

class ExitWhenInactive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        bot_voice_state = member.guild.voice_client

        if bot_voice_state and before.channel == bot_voice_state.channel and after.channel != bot_voice_state.channel:
            for _ in range(300):
                await asyncio.sleep(1)
                if len(bot_voice_state.channel.members) > 1:
                    return
            
            if len(bot_voice_state.channel.members) <= 1:
                if bot_voice_state.is_playing():
                    bot_voice_state.stop()
                
                await bot_voice_state.disconnect()
                queue_manager.get_queue(member.guild.id).clear()
                guild_id = member.guild.id
                if guild_id in previous_now_playing_msgs and previous_now_playing_msgs[guild_id] is not None:
                    try:
                        await previous_now_playing_msgs[guild_id].delete()
                    except Exception as e:
                        print(f"Erro ao deletar mensagem: {e}")
                    del previous_now_playing_msgs[guild_id]

async def setup(bot):
    await bot.add_cog(ExitWhenInactive(bot))
