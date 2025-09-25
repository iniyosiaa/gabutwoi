import os
import threading
import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --------- Discord Bot Event ---------
@bot.event
async def on_ready():
    print(f"✅ Bot online sebagai {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel is None:
        return

    embed = discord.Embed(color=discord.Color.blurple())
    embed.set_author(name=str(member), icon_url=member.display_avatar.url)

    if before.channel is None and after.channel is not None:
        embed.title = "🔊 Voice Join"
        embed.description = f"**{member.display_name}** join **{after.channel.name}**"
    elif before.channel is not None and after.channel is None:
        embed.title = "🔇 Voice Leave"
        embed.description = f"**{member.display_name}** left **{before.channel.name}**"
    elif before.channel != after.channel:
        embed.title = "🔁 Voice Move"
        embed.description = (
            f"**{member.display_name}** pindah dari **{before.channel.name}** "
            f"ke **{after.channel.name}**"
        )
    else:
        changes = []
        if before.self_mute != after.self_mute:
            changes.append("self-mute" if after.self_mute else "unmute")
        if before.self_deaf != after.self_deaf:
            changes.append("self-deaf" if after.self_deaf else "undeaf")

        if not changes:
            return

        embed.title = "🎛 Voice State Change"
        embed.description = f"**{member.display_name}**: {', '.join(changes)}"

    await log_channel.send(embed=embed)

# --------- Flask keep-alive ---------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

def run_flask():
    # listen di semua IP (0.0.0.0) dan port Replit default (biasanya 8080)
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    # Jalankan Flask di thread terpisah biar nggak ngeblokir bot.run
    t = threading.Thread(target=run_flask)
    t.start()

# --------- Start all ---------
keep_alive()
bot.run(TOKEN)