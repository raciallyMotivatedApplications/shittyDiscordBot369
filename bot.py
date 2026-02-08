import discord
from discord.ext import commands, voice_recv
from discord import app_commands
import os
import asyncio
from dotenv import load_dotenv

import logging

# ... imports ...

load_dotenv()

# Suppress noise
logging.getLogger('discord.ext.voice_recv').setLevel(logging.ERROR)
logging.getLogger('discord.voice_state').setLevel(logging.ERROR)
logging.getLogger('discord.gateway').setLevel(logging.ERROR)
logging.getLogger('discord.client').setLevel(logging.ERROR)

TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_USER_ID = 300494697875374081
ALARM_FILE = 'alarm.mp3'

intents = discord.Intents.default()
# intents.message_content = True
# intents.voice_states = True # Included in default? Yes usually.

# Setup bot
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Commands synced")

bot = Bot()

@bot.command()
async def sync(ctx):
    fmt = await ctx.bot.tree.sync()
    await ctx.send(f"Synced {len(fmt)} commands.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.event
async def on_message(message):
    # Don't reply to ourselves
    if message.author == bot.user:
        return

    if message.author.id == TARGET_USER_ID:
        try:
            await message.reply("shut the fuck up faggot")
        except Exception as e:
            print(f"Failed to reply: {e}")

    # Needed if we ever add text-based commands
    # await bot.process_commands(message) 

# Custom sink to listen for specific user
class TargetUserSink(voice_recv.AudioSink):
    def __init__(self, target_id, callback):
        super().__init__()
        self.target_id = target_id
        self.callback = callback

    def wants_opus(self) -> bool:
        return False

    def write(self, user: discord.User, data: voice_recv.VoiceData):
        if user is None:
            return
        if user.id == self.target_id:
            # Trigger callback
            self.callback(user)

    def cleanup(self):
        pass

@bot.tree.command(name="eldricalarm")
@app_commands.describe(seconds="How long the bot should stay in the channel")
async def eldricalarm(interaction: discord.Interaction, seconds: int):
    """Joins your voice channel and listens for the target user."""
    
    if not interaction.user.voice:
        await interaction.response.send_message("You are not in a voice channel!", ephemeral=True)
        return

    channel = interaction.user.voice.channel
    await interaction.response.send_message(f"Joined {channel.name}. Listening for {seconds} seconds...")

    # Join voice channel with voice reception enabled
    try:
        vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
    except discord.ClientException:
        await interaction.followup.send("I'm already in a voice channel!", ephemeral=True)
        return

    stop_event = asyncio.Event()
    
    # State
    is_paused = False
    
    def on_target_speak(user):
        nonlocal is_paused
        if is_paused:
            return
            
        print(f"Target user {user.name} spoke!")
        is_paused = True
        
        # We need to schedule the playback logic on the main loop
        asyncio.run_coroutine_threadsafe(handle_alarm(vc), bot.loop)

    async def handle_alarm(voice_client):
        nonlocal is_paused
        # Play audio
        if voice_client.is_playing():
            voice_client.stop()
            
        if os.path.exists(ALARM_FILE):
            print(f"Playing {ALARM_FILE}")
            
            # Check for local ffmpeg.exe
            executable = "ffmpeg"
            if os.path.exists("ffmpeg.exe"):
                 executable = "./ffmpeg.exe"
                 
            try:
                source = discord.FFmpegPCMAudio(ALARM_FILE, executable=executable)
                voice_client.play(source, after=lambda e: print(f"Player error: {e}") if e else None)
            except Exception as e:
                print(f"Failed to play audio: {e}")
        else:
            print(f"File {ALARM_FILE} not found!")

        # Wait 20 seconds (pausing observation)
        print("Pausing observation for 20 seconds...")
        await asyncio.sleep(20)
        
        print("Resuming observation...")
        is_paused = False

    # Start listening
    vc.listen(TargetUserSink(TARGET_USER_ID, on_target_speak))

    # Wait for the specified duration
    await asyncio.sleep(seconds)
    
    await vc.disconnect()
    await interaction.followup.send("Time's up! Leaving voice channel.")

# Music Queue: guild_id -> list of (url, title)
queues = {}

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = []
    return queues[guild_id]

def play_next(interaction):
    guild_id = interaction.guild_id
    queue = get_queue(guild_id)
    voice_client = interaction.guild.voice_client

    if not voice_client:
        return
        
    if voice_client.is_playing() and not voice_client.is_paused():
        return

    if len(queue) > 0:
        url, title = queue.pop(0)
        print(f"Playing next: {title}")
        
        # We need to run the async play logic from a sync context (after callback) is tricky.
        # So we just prepare the source here or run coroutine.
        # Actually simplest way for simple bot: just use run_coroutine_threadsafe to play.
        
        asyncio.run_coroutine_threadsafe(play_audio(interaction, url, title), bot.loop)
    else:
        print("Queue finished.")

async def play_audio(interaction, url, title):
    voice_client = interaction.guild.voice_client
    if not voice_client:
        return

    executable = "ffmpeg"
    if os.path.exists("ffmpeg.exe"):
            executable = "./ffmpeg.exe"
            
    ffmpeg_opts = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    
    try:
        source = discord.FFmpegPCMAudio(url, executable=executable, **ffmpeg_opts)
        # Define callback to play next
        def after_playing(error):
            if error:
                print(f"Player error: {error}")
            play_next(interaction)
            
        voice_client.play(source, after=after_playing)
        await interaction.channel.send(f"Now playing: **{title}**")
    except Exception as e:
        print(f"Failed to play {title}: {e}")
        play_next(interaction) # Skip if failed

@bot.tree.command(name="zplay")
@app_commands.describe(url="YouTube URL")
async def zplay(interaction: discord.Interaction, url: str):
    """Adds a song to the queue."""
    if not interaction.user.voice:
        await interaction.response.send_message("You are not in a voice channel!", ephemeral=True)
        return

    channel = interaction.user.voice.channel
    await interaction.response.send_message(f"Processing {url}...")

    voice_client = interaction.guild.voice_client
    if not voice_client:
        try:
            voice_client = await channel.connect(cls=voice_recv.VoiceRecvClient)
        except Exception as e:
            await interaction.followup.send(f"Failed to join: {e}")
            return
    else:
        if voice_client.channel != channel:
            await voice_client.move_to(channel)

    # Get info first
    import yt_dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info.get('title', 'Unknown')
            
        queue = get_queue(interaction.guild_id)
        queue.append((audio_url, title))
        
        await interaction.followup.send(f"Added to queue: **{title}**")
        
        if not voice_client.is_playing() and not voice_client.is_paused():
            play_next(interaction)
            
    except Exception as e:
        await interaction.followup.send(f"Error adding to queue: {e}")

@bot.tree.command(name="zskip")
async def zskip(interaction: discord.Interaction):
    """Skips the current song."""
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop() # This triggers the after check which plays next
        await interaction.response.send_message("Skipped!")
    else:
        await interaction.response.send_message("Nothing is playing.")

@bot.tree.command(name="zpause")
async def zpause(interaction: discord.Interaction):
    """Pauses playback."""
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await interaction.response.send_message("Paused.")
    else:
        await interaction.response.send_message("Nothing is playing.")

@bot.tree.command(name="zresume")
async def zresume(interaction: discord.Interaction):
    """Resumes playback."""
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("Resumed.")
    else:
        await interaction.response.send_message("Not paused.")

@bot.tree.command(name="zstop")
async def zstop(interaction: discord.Interaction):
    """Clears queue, stops playback, and disconnects."""
    voice_client = interaction.guild.voice_client
    
    # Clear queue
    if interaction.guild_id in queues:
        queues[interaction.guild_id] = []
        
    if voice_client:
        voice_client.stop()
        await voice_client.disconnect()
        await interaction.response.send_message("Stopped, cleared queue, and disconnected.")
    else:
        await interaction.response.send_message("I'm not in a voice channel.")

if __name__ == '__main__':
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in .env")
    else:
        bot.run(TOKEN)
