import discord
import responses
from responses import active_sessions

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
    TOKEN = 'OTAwNjcyNDg3NzUzNDEyNjI4.Gq3lU8.Sy4EUpQAiRNsqgzy3Ko9sRFL__w21LUb4bYfnc'
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