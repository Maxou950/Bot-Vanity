import discord
from discord.ext import commands
import requests
import os

TOKEN = os.getenv("DISCORD_TOKEN")

REACTIONS = {
    "💋": "Kiss",
    "💍": "Marry",
    "🔪": "Kill"
}

# ✅ Endpoint avec beaucoup plus de chances d'avoir un nom/anime
API_URL = "https://nekos.best/api/v2/waifu"

intents = discord.Intents.default()
intents.members = True


class MyBot(commands.Bot):
    def __init__(self):
        # On garde un prefix "!" juste pour éviter des erreurs internes, mais on utilise /kmk
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sync des slash commands
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

        if r.status_code != 200:
            print(f"[API] Status not OK: {r.status_code} - {r.text[:120]}")
            return None

        ctype = r.headers.get("Content-Type", "")
        if "application/json" not in ctype:
            print(f"[API] Unexpected content-type: {ctype}")
            print(r.text[:200])
            return None

        data = r.json()["results"][0]

        name = (data.get("character_name") or "").strip()
        anime = (data.get("anime_name") or "").strip()

        return {
            "name": name,
            "anime": anime,
            "image": data["url"]
        }

    except Exception as e:
        print("[API] ERROR:", repr(e))
        return None


def format_line(c: dict) -> str:
    """
    Affichage propre :
    - Nom + anime si dispo
    - Sinon juste nom
    - Sinon juste anime
    - Sinon 'Perso mystère' (sans spam d'Inconnu)
    """
    name = (c.get("name") or "").strip()
    anime = (c.get("anime") or "").strip()

    if name and anime:
        return f"**{name}**\n*{anime}*"
    if name:
        return f"**{name}**"
    if anime:
        return f"*{anime}*"
    return "🎲 Perso mystère"


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

    embed.add_field(name="💋 Kiss", value=format_line(kiss), inline=True)
    embed.add_field(name="💍 Marry", value=format_line(marry), inline=True)
    embed.add_field(name="🔪 Kill", value=format_line(kill), inline=True)

    # ✅ Une seule image affichée (plus de photo différente en haut à droite)
    embed.set_image(url=kiss["image"])
    # embed.set_thumbnail(url=marry["image"])  # ❌ retiré volontairement
    embed.set_footer(text="🔪 en dernier")

    # ✅ IMPORTANT : récupérer le message envoyé par followup pour ajouter les réactions dessus
    sent_msg = await interaction.followup.send(embed=embed, wait=True)

    # ✅ Ajout des réactions (avec logs si Discord refuse)
    try:
        for emoji in REACTIONS:
            await sent_msg.add_reaction(emoji)
    except Exception as e:
        print("REACTION ERROR:", repr(e))


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