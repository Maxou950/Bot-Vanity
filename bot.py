import discord
from discord.ext import commands
from discord import app_commands
import requests
import os

TOKEN = os.getenv("DISCORD_TOKEN")

REACTIONS = {
    "💋": "Kiss",
    "💍": "Marry",
    "🔪": "Kill"
}

API_URL = "https://nekos.best/api/v2/neko"

intents = discord.Intents.default()
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=None, intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

def get_character():
    data = requests.get(API_URL).json()["results"][0]
    return {
        "name": data["character_name"],
        "anime": data["anime_name"],
        "image": data["url"]
    }

@bot.tree.command(name="kmk", description="Kiss / Marry / Kill avec des persos d'animé")
async def kmk(interaction: discord.Interaction):
    kiss = get_character()
    marry = get_character()
    kill = get_character()

    embed = discord.Embed(
        title="💋💍🔪 Kiss / Marry / Kill",
        description="Réagis pour choisir ton destin.",
        color=0xff5fa2
    )

    embed.add_field(
        name="💋 Kiss",
        value=f"**{kiss['name']}**\n*{kiss['anime']}*",
        inline=True
    )
    embed.add_field(
        name="💍 Marry",
        value=f"**{marry['name']}**\n*{marry['anime']}*",
        inline=True
    )
    embed.add_field(
        name="🔪 Kill",
        value=f"**{kill['name']}**\n*{kill['anime']}*",
        inline=True
    )

    embed.set_image(url=kiss["image"])
    embed.set_thumbnail(url=marry["image"])
    embed.set_footer(text="🔪 en dernier")

    await interaction.response.send_message(embed=embed)

    msg = await interaction.original_response()
    for emoji in REACTIONS:
        await msg.add_reaction(emoji)

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