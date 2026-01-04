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
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

def get_character():
    """
    Retourne un dict {name, anime, image} ou None si l'API échoue / est bloquée.
    """
    try:
        r = requests.get(
            API_URL,
            timeout=6,
            headers={"User-Agent": "DiscordBot KMK (Render)"},
        )

        # Si Cloudflare / blocage / autre statut
        if r.status_code != 200:
            print(f"[API] Status not OK: {r.status_code} - {r.text[:120]}")
            return None

        # Si l'API renvoie une page HTML au lieu de JSON (Cloudflare)
        ctype = r.headers.get("Content-Type", "")
        if "application/json" not in ctype:
            print(f"[API] Unexpected content-type: {ctype}")
            print(r.text[:200])
            return None

        data = r.json()["results"][0]
        return {
            "name": data.get("character_name") or "Inconnu",
            "anime": data.get("anime_name") or "Inconnu",
            "image": data["url"]
        }

    except Exception as e:
        print("[API] ERROR:", repr(e))
        return None

@bot.tree.command(name="kmk", description="Kiss / Marry / Kill avec des persos d'animé")
async def kmk(interaction: discord.Interaction):
    # ✅ Anti-timeout Discord (3s)
    await interaction.response.defer()

    kiss = get_character()
    marry = get_character()
    kill = get_character()

    # ✅ Si l'API est bloquée / lente / KO, on répond quand même
    if not kiss or not marry or not kill:
        await interaction.followup.send(
            "❌ Je n’arrive pas à récupérer des persos (API bloquée/instable). Réessaie dans 1-2 minutes 🙏"
        )
        return

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

    # ✅ Après defer() -> followup
    await interaction.followup.send(embed=embed)

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