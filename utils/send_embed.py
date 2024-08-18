import discord

async def send_simple_embed(ctx, description, color):
    embed = discord.Embed(description=description, color=color)
    return await ctx.send(embed=embed)