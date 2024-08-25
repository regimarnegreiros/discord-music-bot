import discord
from discord.ext import commands
from discord.ui import Button, View

from config.settings import PREFIX

if not PREFIX:
    raise ValueError("O PREFIX não foi encontrado. Verifique o arquivo config.py.")

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
        bot.remove_command('help')  # Remove o comando de ajuda padrão

    def create_command_list(self, commands_with_titles):
        commands_info = []
        for command_name, custom_title in commands_with_titles:
            command = self.bot.get_command(command_name)
            if not command:
                continue

            aliases = command.aliases
            description = command.description or "Nenhuma descrição fornecida."
            aliases_str = ", ".join([f"{PREFIX}{alias}" for alias in aliases])
            
            # Utilize o título personalizado se fornecido, caso contrário, o nome do comando
            command_display_name = f"{PREFIX}{custom_title}" if custom_title else f"{PREFIX}{command_name}"
            command_info = f"**{command_display_name}**: {description}"
            if aliases:
                command_info += f"\n``Alias: {aliases_str}``"
            commands_info.append(command_info)
        
        return "\n".join(commands_info)

    @commands.hybrid_command(aliases=['ajuda', 'h'], description="Exibe os comandos existentes.")
    async def help(self, ctx: commands.Context):
        # Tópicos de comandos com nomes de comandos e títulos personalizados (opcionais)
        topics = {
            "💎 Comandos Básicos": [
                ('play', 'play [link/nome]'),
                ('skip', None),
                ('queue', None),
            ],
            "🎵 Plataformas": [
                ('spotify', 'spotify [link/nome]'),
                ('youtube', 'youtube [link/nome]'),
                ('deezer', 'deezer [link/nome]')
            ],
            "🎶 Comandos de Fila": [
                ('queue', None),
                ('skipto', None),
                ('remove', 'remove [index]'),
                ('move', 'move [de_index] [para_index]'),
                ('shuffle', None),
                ('clearqueue', None)
            ],
            "🔗 Comandos de Conexão": [
                ('join', None),
                ('exit', None)
            ]
        }

        # Criar embeds para cada tópico
        pages = []
        for topic, commands_with_titles in topics.items():
            command_list = self.create_command_list(commands_with_titles)
            embed = discord.Embed(
                title=topic,
                description=command_list,
                color=discord.Color.blue()
            )
            pages.append(embed)

        current_page = 0

        # Atualiza a mensagem e desativa botões conforme necessário
        async def update_message(interaction):
            # Atualiza os estados dos botões
            prev_button.disabled = current_page == 0
            next_button.disabled = current_page == len(pages) - 1
            await interaction.response.edit_message(embed=pages[current_page], view=view)

        # Definição dos botões de navegação
        prev_button = Button(label="<", style=discord.ButtonStyle.gray)
        next_button = Button(label=">", style=discord.ButtonStyle.gray)

        # Funções de callback para os botões
        async def prev_button_callback(interaction):
            nonlocal current_page
            if current_page > 0:
                current_page -= 1
                await update_message(interaction)

        async def next_button_callback(interaction):
            nonlocal current_page
            if current_page < len(pages) - 1:
                current_page += 1
                await update_message(interaction)

        # Atribuir os callbacks aos botões
        prev_button.callback = prev_button_callback
        next_button.callback = next_button_callback

        # Desativar o botão 'Anterior' se estiver na primeira página
        prev_button.disabled = current_page == 0
        # Desativar o botão 'Próximo' se estiver na última página
        next_button.disabled = current_page == len(pages) - 1

        # Cria uma nova View com um timeout de 60 segundos
        view = View(timeout=60)
        view.add_item(prev_button)
        view.add_item(next_button)

        # Sobrescreve o método on_timeout para apagar a mensagem após 1 minuto sem interação
        async def on_timeout():
            if view.message:
                await view.message.delete()

        # Atribui a função on_timeout à view
        view.on_timeout = on_timeout

        # Envia o embed inicial com os botões
        view.message = await ctx.send(embed=pages[current_page], view=view, silent=True)

async def setup(bot):
    await bot.add_cog(Help(bot))
