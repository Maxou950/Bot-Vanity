import discord
from discord.ext import commands
import requests
from config import TOKEN, REACTIONS, WAIFU_API

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def get_random_anime():
    response = requests.get(WAIFU_API)
    return response.json()["url"]

@bot.event
async def on_ready():
    print(f"✅ Bot connecté : {bot.user}")

@bot.command()
async def kmk(ctx):
    kiss = get_random_anime()
    marry = get_random_anime()
    kill = get_random_anime()

    embed = discord.Embed(
        title="💋💍🔪 Kiss / Marry / Kill",
        description="Réagis pour choisir ton destin.",
        color=0xff5fa2
    )

    embed.add_field(name="💋 Kiss", value="\u200b", inline=True)
    embed.add_field(name="💍 Marry", value="\u200b", inline=True)
    embed.add_field(name="🔪 Kill", value="\u200b", inline=True)

    embed.set_image(url=kiss)
    embed.set_thumbnail(url=marry)
    embed.set_footer(text="🔪 en dernier message")

    msg1 = await ctx.send(embed=embed)
    await ctx.send(kill)

    for emoji in REACTIONS:
        await msg1.add_reaction(emoji)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    role_name = REACTIONS.get(str(reaction.emoji))
    if not role_name:
        return

    guild = reaction.message.guild
    role = discord.utils.get(guild.roles, name=role_name)

    if not role:
        role = await guild.create_role(name=role_name)

    await user.add_roles(role)

bot.run(TOKEN)