from discord.ext import commands
from config.colors import COLOR

class ChannelLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Verificar se o usuário entrou em um canal de voz
        if before.channel is None and after.channel is not None:
            channel_name = after.channel.name
            print(f'{COLOR["BOLD_WHITE"]}{member.display_name}{COLOR["RESET"]} entrou: {COLOR["BOLD_WHITE"]}{channel_name}{COLOR["RESET"]}')

        # Verificar se o usuário saiu de um canal de voz
        elif before.channel is not None and after.channel is None:
            channel_name = before.channel.name
            print(f'{COLOR["BOLD_WHITE"]}{member.display_name}{COLOR["RESET"]} saiu: {COLOR["BOLD_WHITE"]}{channel_name}{COLOR["RESET"]}')

        # Verificar se o usuário mudou de canal de voz
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            old_channel_name = before.channel.name
            new_channel_name = after.channel.name
            print(f'{COLOR["BOLD_WHITE"]}{member.display_name}{COLOR["RESET"]} trocou: {COLOR["BOLD_WHITE"]}{old_channel_name}{COLOR["RESET"]} para {COLOR["BOLD_WHITE"]}{new_channel_name}{COLOR["RESET"]}')

async def setup(bot):
    await bot.add_cog(ChannelLog(bot))
