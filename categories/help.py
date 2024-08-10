import discord
from discord import app_commands
from discord.ext import commands

from config import PREFIX

if not PREFIX:
    raise ValueError("O PREFIX não foi encontrado. Verifique o arquivo config.py.")

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
        bot.remove_command('help')  # Remove o comando de ajuda padrão

    def create_command_field(self, command_name, custom_title=None):
        command = self.bot.get_command(command_name)
        if not command:
            return None

        aliases = command.aliases
        description = command.description or "Nenhuma descrição fornecida."
        aliases_str = ", ".join([f"{PREFIX}{alias}" for alias in aliases])
        field_name = f"{PREFIX}{custom_title}" if custom_title else f"{PREFIX}{command.name}"
        
        field_value = f"{description}\nComandos alternativos: {aliases_str}" if aliases else description
        
        return {"name": field_name, "value": field_value, "inline": False}

    @commands.hybrid_command(aliases=['ajuda', 'h'], description="Exibe os comandos existentes.")
    async def help(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Lista de Comandos",
            color=discord.Color.blue()
        )

        # Tópicos de comandos
        topics = {
            "🎵 Comandos de Música": [
                ('play', 'play [link/nome da música]'),
                ('spotify', 'spotify [link/nome da música]'),
                ('skip', 'skip [quantidade (opcional)]')
            ],
            "🎶 Comandos de Fila": [
                ('queue', None),
                ('remove', 'remove [index]'),
                ('move', 'move [de_index] [para_index]'),
                ('clear', None),
                ('random', None)
            ],
            "🔗 Comandos de Conexão": [
                ('join', None),
                ('exit', None)
            ]
        }

        for topic, commands_in_order in topics.items():
            embed.add_field(name="\u200b", value=f"**{topic}**", inline=False)
            for command_name, custom_title in commands_in_order:
                field = self.create_command_field(command_name, custom_title)
                if field:
                    embed.add_field(**field)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
