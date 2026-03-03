import discord
import random
import asyncio
import json
import math
import aiohttp  # Replaces requests, built into discord.py
from spellchecker import SpellChecker

active_sessions = set()
spell = SpellChecker()

# Add your Hugging Face API Token here!
HF_API_KEY = "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"
API_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-mpnet-base-v2"

# Load the JSON data
with open('word_pool.json', 'r', encoding='utf-8') as f:
    word_data = json.load(f)

word_pools = word_data['themes']

# Build a fast dictionary of coordinates from your JSON pool
country_coords = {}
for item in word_pools.get('countries', []):
    country_coords[item['target']] = (item.get('lat', 0), item.get('lon', 0))

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return int(R * c)  # Returns distance in km

# Added "channel" as a parameter so we can send UI updates
async def get_nlp_score(guess, target_word, target_context, channel=None):
    guess = guess.strip()

    if guess.lower() == target_word.lower():
        return 100

    target_phrase = f"{target_word}: {target_context}"
    payload = {
        "inputs": {
            "source_sentence": guess,
            "sentences": [target_phrase, target_word]
        }
    }
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    best_raw_score = 0
    max_retries = 3  # Try a maximum of 3 times before giving up

    # --- THE RETRY LOOP ---
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, headers=headers, json=payload) as response:

                    if response.status == 200:
                        # Success! The model is awake and did the math.
                        scores = await response.json()
                        best_raw_score = max(scores)
                        break  # Break out of the retry loop

                    elif response.status == 503:
                        # The model is asleep. Grab the estimated wait time.
                        error_data = await response.json()
                        wait_time = error_data.get("estimated_time", 15.0)

                        if channel:
                            # Tell the user we are waking up the AI
                            temp_embed = discord.Embed(
                                description=f"⏳ **Waking up the AI...** this will take about {int(wait_time)} seconds.",
                                color=discord.Color.dark_grey()
                            )
                            temp_msg = await channel.send(embed=temp_embed)

                        # Pause the bot for the exact time Hugging Face requested
                        await asyncio.sleep(wait_time)

                        if channel:
                            # Delete the temporary message before trying again
                            await temp_msg.delete()

                    else:
                        print(f"API Error: {response.status}")
                        return 0  # Failsafe

        except Exception as e:
            print(f"Request Error: {e}")
            return 0  # Failsafe

    # --- THE MATH SCALING ---
    min_threshold = 0.15

    if best_raw_score < min_threshold:
        semantic_percentage = 0
    else:
        semantic_percentage = ((best_raw_score - min_threshold) / (1.0 - min_threshold)) * 100

    final_score = int(semantic_percentage)

    if len(guess) > 3 and guess.lower() in target_context.lower():
        final_score = max(final_score, 65)

    return max(0, min(99, final_score))

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

    if p_message == 'kys' or p_message == 'kill yourself' or p_message == 'keep yourself safe' or p_message == 'sky ginger':
        return 'https://tenor.com/view/love-gif-1725081057622358733'

    if 'reyes' in p_message or 'gayes' in p_message:
        return 'https://cdn.discordapp.com/attachments/867612417993998338/1392929172690829383/IMG-20240411-WA0009.jpg?ex=687151e2&is=68700062&hm=e3fa1fed8d03fdbd1395e18edb7a1b766b15023e72808c87de8f14024004fe8f&'

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
                # --- YOUR EXISTING CODE STAYS EXACTLY THE SAME ---
                response = await client.wait_for('message', check=check, timeout=30.0)
                response_embed = discord.Embed(
                    description=f'You selected: **{response.content}**',
                    color=discord.Color.orange()
                )
                response_embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                await message.channel.send(embed=response_embed)

                # 1. Fetch the target word and context based on the 2nd JSON approach
                theme_selected = response.content.lower()
                selected_item = random.choice(word_pools[theme_selected])
                target_word = selected_item['target']
                target_context = selected_item['context']
                print(f"The bot has chosen {target_word}")
                attempts = 20

                # 2. Send the NEW embed telling them to start guessing
                game_embed = discord.Embed(
                    title="Guess the Word!",
                    description=(
                        f"I have a word in mind for **{theme_selected.capitalize()}**.\n"
                        f"Type your guess below!\n\n"
                        f"**Attempts remaining:** {attempts}"
                    ),
                    color=discord.Color.blue()
                )
                game_embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                await message.channel.send(embed=game_embed)

                # 3. Setup the check for the guessing loop
                def guess_check(m):
                    return m.author == message.author and m.channel == message.channel

                # 4. The Guessing Loop
                while attempts > 0:
                    try:
                        # Wait for the user to type a guess (60 second timeout per guess)
                        guess_msg = await client.wait_for('message', check=guess_check, timeout=60.0)
                        guess_text = guess_msg.content.lower().strip()

                        words_in_guess = guess_text.split()
                        known_words = spell.known(words_in_guess)

                        if len(known_words) != len(words_in_guess) and guess_text != target_word:
                            attempts -= 1

                            if attempts > 0:
                                unknown_embed = discord.Embed(
                                    title="Word Not Recognized",
                                    description=(
                                        f"I could not interpret your word, which gives a score of **0%**\n\n"
                                        f"**Attempts remaining:** {attempts}"
                                    ),
                                    color=discord.Color.dark_grey()
                                )
                                unknown_embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                                await message.channel.send(embed=unknown_embed)
                            else:
                                # Handle the edge case where their gibberish was their last attempt
                                lose_embed = discord.Embed(
                                    title="Game Over",
                                    description=(
                                        f"I could not interpret your word, which gives a score of **0%**\n\n"
                                        f"You've run out of attempts. The word was: **{target_word}**"
                                    ),
                                    color=discord.Color.red()
                                )
                                lose_embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                                await message.channel.send(embed=lose_embed)

                            continue

                        # --- HYBRID SCORING ENGINE ---
                        distance_km = None  # Keep track of this for the UI

                        if theme_selected == "countries" and guess_text in country_coords:
                            # 1. It's a country guess! Use Geographical Distance Scoring
                            target_lat, target_lon = country_coords[target_word]
                            guess_lat, guess_lon = country_coords[guess_text]

                            distance_km = calculate_distance(guess_lat, guess_lon, target_lat, target_lon)

                            if distance_km == 0:
                                score = 100
                            else:
                                # Map the distance to a percentage (Max penalty around 15,000 km)
                                score = max(0, int(100 - (distance_km / 150)))
                        else:
                            # 2. It's an adjective or a different theme! Use Hugging Face API
                            score = await get_nlp_score(guess_text, target_word, target_context, message.channel)

                        attempts -= 1

                        # 5. Handle Outcomes and send a new message
                        if score == 100:
                            win_embed = discord.Embed(
                                title="🎉 You Win!",
                                description=(
                                    f"I interpreted your guess as `{guess_text}`, which gives a score of **100%**!\n\n"
                                    f"Congrats, you guessed the word: **{target_word}**"
                                ),
                                color=discord.Color.green()
                            )
                            win_embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                            await message.channel.send(embed=win_embed)
                            break  # Exit the loop, game is over

                        elif attempts > 0:
                            # Create a dynamic message depending on if it was a distance guess or an NLP guess
                            if distance_km is not None:
                                feedback_msg = f"I interpreted your guess as `{guess_text}`. It is **{distance_km} km** away, giving a score of **{score}%**"
                            else:
                                feedback_msg = f"I interpreted your guess as `{guess_text}`, which gives a score of **{score}%**"

                            fail_embed = discord.Embed(
                                title="Keep Guessing!",
                                description=(
                                    f"{feedback_msg}\n\n"
                                    f"**Attempts remaining:** {attempts}"
                                ),
                                color=discord.Color.orange()
                            )
                            fail_embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                            await message.channel.send(embed=fail_embed)

                        else:
                            # Dynamic message for losing on the last attempt
                            if distance_km is not None:
                                feedback_msg = f"I interpreted your guess as `{guess_text}`. It is **{distance_km} km** away, giving a score of **{score}%**"
                            else:
                                feedback_msg = f"I interpreted your guess as `{guess_text}`, which gives a score of **{score}%**"

                            lose_embed = discord.Embed(
                                title="Game Over",
                                description=(
                                    f"{feedback_msg}\n\n"
                                    f"You've run out of attempts. The word was: **{target_word}**"
                                ),
                                color=discord.Color.red()
                            )
                            lose_embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                            await message.channel.send(embed=lose_embed)

                    except asyncio.TimeoutError:
                        # This triggers if they take too long to make a guess
                        timeout_embed = discord.Embed(
                            title="Session Timed Out",
                            description="You took too long to guess, terminating session.",
                            color=discord.Color.red()
                        )
                        timeout_embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                        await message.channel.send(embed=timeout_embed)
                        break  # Exit the loop

            except asyncio.TimeoutError:
                # This triggers if they take too long to pick a theme (your existing logic)
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