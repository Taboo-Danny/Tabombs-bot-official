import discord
import responses
from responses import active_sessions
from dotenv import load_dotenv
import os
import asyncio
import time

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

async def send_message(message, is_private):
    try:
        response = responses.handle_response(message)
        if is_private:
            if isinstance(response, discord.Embed):
                await message.author.send(embed=response)
            else:
                await message.author.send(response)
        else:
            if isinstance(response, discord.Embed):
                await message.channel.send(embed=response)
            else:
                await message.channel.send(response)
    except Exception as e:
        print(e)

def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True  # Needed to read message content
    client = discord.Client(intents = intents)

    @client.event
    async def on_ready():
        # Set status and activity
        await client.change_presence(
            status = discord.Status.idle,  # Options: online, idle, dnd, invisible
            activity = discord.Game('Type "<help" for my list of commands')  # Other options: Game, Streaming, Listening, Watching
        )
        print(f'{client.user} has connected to Discord!')
        
        # Start background task to check uptime and DM the owner after 3 days
        asyncio.create_task(uptime_checker(client))

async def uptime_checker(client):
    await client.wait_until_ready()
    start_time = time.time()
    three_days = 3 * 24 * 60 * 60  # 259200 seconds
    sent = False
    
    while not client.is_closed():
        elapsed = time.time() - start_time
        if elapsed >= three_days and not sent:
            try:
                app_info = await client.application_info()
                owner = app_info.owner
                
                embed = discord.Embed(
                    title="🚀 Bot Uptime Milestone!",
                    description="Your bot has been up and running continuously for **3 days**! 🎉",
                    color=discord.Color.green()
                )
                await owner.send(embed=embed)
                sent = True
            except Exception as e:
                print(f"Failed to send uptime DM to owner: {e}")
        await asyncio.sleep(3600)  # Check every hour

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if isinstance(message.channel, discord.DMChannel):
            return

        user_message = message.content.lower()
        user_id = message.author.id

        # 🔒 Block all commands if user is in an active session
        if user_id in active_sessions:
            return
        if user_message[1:] == 'play':
            await responses.play_command(client, message)
            return
        await send_message(message, False)

    client.run(TOKEN)