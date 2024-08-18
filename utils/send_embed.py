import discord

async def send_simple_embed(ctx, description, color, silent=True):
    embed = discord.Embed(description=description, color=color)
    return await ctx.send(embed=embed, silent=silent)