import discord
from discord.ext import commands
from utils.is_url import *
from utils.queue_manager import queue_manager
from utils.send_embed import *

class QueueView(discord.ui.View):
    def __init__(self, ctx: commands.Context, queue: list):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.queue = queue
        self.page = 0
        self.items_per_page = 10  # número de músicas por página
        self.max_page = (len(queue) - 1) // self.items_per_page

        # Desabilita todos os botões se houver apenas uma página
        if self.max_page == 0:
            for button in self.children:
                button.disabled = True

    async def send_queue_page(self):
        # Verifica se a fila está vazia
        if not self.queue:
            embed = discord.Embed(
                description="A fila de músicas está vazia. Adicione algumas músicas para ver a lista!",
                color=discord.Color.blue()
            )
            if hasattr(self, 'message'):
                await self.message.edit(content=None, embed=embed, view=None)
            else:
                self.message = await self.ctx.send(embed=embed)
            return

        start = self.page * self.items_per_page
        end = start + self.items_per_page
        queue_list = '\n'.join([f'{idx+1}. {song_info["title"]}' for idx, song_info in enumerate(self.queue[start:end], start=start)])
        remaining_songs = len(self.queue) - end
        message_content = f'```{queue_list}```'
        if remaining_songs > 0:
            message_content += f'```\n...e mais {remaining_songs} músicas na fila.```'

        if not hasattr(self, 'message'):
            self.message = await self.ctx.send(content=message_content, view=self)
        else:
            await self.message.edit(content=message_content, embed=None, view=self)

    @discord.ui.button(label="<<", style=discord.ButtonStyle.blurple, disabled=True)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = 0
        await self.update_buttons()
        await self.send_queue_page()
        await interaction.response.defer()

    @discord.ui.button(label="<", style=discord.ButtonStyle.gray, disabled=True)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self.max_page = (len(self.queue) - 1) // self.items_per_page
        if self.page > self.max_page:
            self.page = self.max_page
        await self.update_buttons()
        await self.send_queue_page()
        await interaction.response.defer()

    @discord.ui.button(label=">", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self.max_page = (len(self.queue) - 1) // self.items_per_page
        if self.page > self.max_page:
            self.page = self.max_page
        await self.update_buttons()
        await self.send_queue_page()
        await interaction.response.defer()

    @discord.ui.button(label=">>", style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = self.max_page
        self.max_page = (len(self.queue) - 1) // self.items_per_page
        if self.page > self.max_page:
            self.page = self.max_page
        await self.update_buttons()
        await self.send_queue_page()
        await interaction.response.defer()

    async def update_buttons(self):
        self.children[0].disabled = self.page <= 0
        self.children[1].disabled = self.page <= 0
        self.children[2].disabled = self.page >= self.max_page
        self.children[3].disabled = self.page >= self.max_page

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.ctx.author

    async def on_timeout(self):
        # Remove a view (desabilitando os botões) e edita a mensagem para indicar que expirou
        for item in self.children:
            item.disabled = True
        if hasattr(self, 'message'):
            embed = discord.Embed(
                description="Tempo esgotado! Utilize o comando novamente para ver a fila.",
                color=discord.Color.blue()
            )
            await self.message.edit(content=None,embed=embed, view=None)

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
        
        view = QueueView(ctx, queue)
        await view.send_queue_page()

async def setup(bot):
    await bot.add_cog(Queue(bot))
