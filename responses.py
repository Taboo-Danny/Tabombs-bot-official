import discord
import random
import asyncio

active_sessions = set()

def handle_response(message):
    p_message = message.content.lower()

    if p_message == 'yogurt' or p_message == 'yo gurt':
        return 'gurt: yo!'

    if p_message == 'fuck you':
        return 'fuck you too!'

    if p_message == 'taboo':
        return 'Danny'

    if 'sex' in p_message:
        return 'Hey guys, did you know that in terms of male human and female Pokémon breeding, Vaporeon is the most compatible Pokémon for humans? Not only are they in the field egg group, which is mostly comprised of mammals, Vaporeon are an average of 3”03’ tall and 63.9 pounds, this means they’re large enough to be able handle human dicks, and with their impressive Base Stats for HP and access to Acid Armor, you can be rough with one. Due to their mostly water based biology, there’s no doubt in my mind that an aroused Vaporeon would be incredibly wet, so wet that you could easily have sex with one for hours without getting sore. They can also learn the moves Attract, Baby-Doll Eyes, Captivate, Charm, and Tail Whip, along with not having fur to hide nipples, so it’d be incredibly easy for one to get you in the mood. With their abilities Water Absorb and Hydration, they can easily recover from fatigue with enough water. No other Pokémon comes close to this level of compatibility. Also, fun fact, if you pull out enough, you can make your Vaporeon turn white. Vaporeon is literally built for human dick. Ungodly defense stat+high HP pool+Acid Armor means it can take cock all day, all shapes and sizes and still come for more'

    if 'speed' in p_message or 'homeless' in p_message:
        return 'https://tenor.com/view/ishowspeed-try-not-to-laugh-gif-7682731162751353849'

    if p_message == 'kys' or p_message == 'kill yourself' or p_message == 'keep yourself safe':
        return 'https://tenor.com/view/love-gif-1725081057622358733'

    if p_message[0] == '<' and p_message[1] != '@':
        if p_message[1:] == 'help':
            embed = discord.Embed(
                title = 'Tabombs bot commands',
                description = 'I am a discord bot made by Taboo Danny for experiments and shit. Here are some of my commands'
                              '\n\n**<play**'
                              '\nEnables the user to play the guessing game, only one session can be done per user at a time'
                              '\n\n**<howtoplay**'
                              '\nGives you a guide on how to play the game and what to expect'
                              '\n\n**<randomfact**'
                              '\nGives you a random fact, can be about anything'
                              '\n\n**<invite**'
                              '\nProvides the URL to enable users to invite me to other servers',
                color = discord.Color.orange()
            )
            return embed
        elif p_message[1:] == 'howtoplay':
            embed = discord.Embed(
                title = 'How to play',
                description = 'These are the rules and what\'s gonna happen in the game'
                              '\n\n1. Depending on the theme you pick, I will have an answer within that theme in mind, and you have 20 attempts to guess what I am thinking of'
                              '\n\n2. When guessing, type in a query/message which I will try to interpret'
                              '\n\n3. Depending on what you answered and what I\'ve interpreted, I will give a score between 0 and 100 - 0 being completely irrelevant and 100 being the correct answer. In short, the higher your score, the closer you are to the answer'
                              '\n\n4. Good luck!',
                color = discord.Color.orange()
            )
            return embed
        elif p_message[1:] == 'randomfact':
            # Open and read all lines
            with open('facts.txt', 'r') as file:
                lines = file.readlines()

            # Choose a random line
            random_line = random.choice(lines).strip()  # .strip() removes newline and spaces
            embed = discord.Embed(
                title = 'Did you know?',
                description = random_line,
                color = discord.Color.orange()
            )
            return embed
        elif p_message[1:] == 'invite':
            embed = discord.Embed(
                title='Invite me',
                description = 'This is my invite URL, have fun!'
                              '\nhttps://discord.com/oauth2/authorize?client_id=900672487753412628&permissions=8&integration_type=0&scope=bot',
                color = discord.Color.orange()
            )
            return embed
        else:
            embed = discord.Embed(
                description = 'I do not understand this command, type "<help" to get the list of commands',
                color=discord.Color.orange()
            )
            return embed

async def play_command(client, message):
    user_message = message.content.lower()
    user_id = message.author.id
    if user_message[0] == '<' and user_message[1] != '@':
        if user_message[1:] == 'play':
            active_sessions.add(user_id)  # 🔒 Lock session

            embed = discord.Embed(
                description=(
                    'These are the themes available currently. Please select one of them '
                    '(type them exactly, not case sensitive):'
                    '\n1. Fruits'
                    '\n2. Countries'
                    '\n3. Household objects'
                ),
                color=discord.Color.orange()
            )
            embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
            await message.channel.send(embed=embed)

            def check(m):
                return (
                        m.author == message.author and
                        m.channel == message.channel and
                        m.content.lower() in ['fruits', 'countries', 'household objects']
                )

            try:
                response = await client.wait_for('message', check=check, timeout=5.0)
                response_embed = discord.Embed(
                    description=f'You selected: **{response.content}**',
                    color=discord.Color.orange()
                )
                response_embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                await message.channel.send(embed=response_embed)

                # Add more logic here as needed...

            except asyncio.TimeoutError:
                response_embed = discord.Embed(
                    title="Session Timed Out",
                    description='You took too long to respond, terminating session.',
                    color=discord.Color.red()
                )
                response_embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                await message.channel.send(embed=response_embed)

            finally:
                active_sessions.discard(user_id)

            return