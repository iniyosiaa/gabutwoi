import os
import threading
from datetime import datetime

import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask

# ====== Load environment ======
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

# ====== Discord Intents & Bot ======
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True  # penting untuk monitor voice channel

bot = commands.Bot(command_prefix="!", intents=intents)

# ====== Flask keep-alive ======
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!", 200

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()

# ====== Discord Events ======
@bot.event
async def on_ready():
    print(f"✅ Bot online sebagai {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    """Log semua aktivitas voice: join, leave, move, mute/unmute."""
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel is None:
        return

    embed = discord.Embed(color=discord.Color.blurple())
    embed.set_author(name=str(member), icon_url=member.display_avatar.url)

    # --- Join voice ---
    if before.channel is None and after.channel is not None:
        embed.title = "🔊 Voice Join"
        embed.description = (
            f"{member.mention} joined {after.channel.mention}"
        )

    # --- Leave voice ---
    elif before.channel is not None and after.channel is None:
        embed.title = "🔇 Voice Leave"
        embed.description = (
            f"{member.mention} left {before.channel.mention}"
        )

    # --- Move voice ---
    elif before.channel != after.channel:
        embed.title = "🔁 Voice Move"
        embed.description = (
            f"{member.mention} moved {before.channel.mention} "
            f"ke {after.channel.mention}"
        )

    # --- Mute/Deafen change ---
    else:
        changes = []
        if before.self_mute != after.self_mute:
            changes.append("self-mute" if after.self_mute else "unmute")
        if before.self_deaf != after.self_deaf:
            changes.append("self-deaf" if after.self_deaf else "undeaf")
        if not changes:
            return  
        embed.title = "🎙️ Voice State Change"
        embed.description = f"{member.mention}: {', '.join(changes)}"

    embed.timestamp = datetime.utcnow()
    await log_channel.send(embed=embed)

# ====== Run both Flask and Bot ======
keep_alive()
bot.run(TOKEN)
