import discord
import random
import asyncio
import json
from spellchecker import SpellChecker
from sentence_transformers import SentenceTransformer, util

active_sessions = set()
spell = SpellChecker()
model = SentenceTransformer('all-mpnet-base-v2')

def get_nlp_score(guess, target_word, target_embedding):
    guess = guess.strip()

    # Hard bypass for exact matches
    if guess.lower() == target_word.lower():
        return 100

    # Convert text to mathematical vectors
    guess_embedding = model.encode(guess)

    # Calculate raw cosine similarity (returns a value usually between -1.0 and 1.0)
    raw_score = util.cos_sim(guess_embedding, target_embedding).item()

    # Mathematical Scaling to make it feel like a real game
    min_threshold = 0.25  # Anything below this raw score is considered complete garbage

    if raw_score < min_threshold:
        final_percentage = 0
    else:
        # Stretch the remaining range (0.25 to 1.0) into a clean 0 to 100 scale
        final_percentage = ((raw_score - min_threshold) / (1.0 - min_threshold)) * 100

    # Cap the score at 99% so players only get 100% for the exact word
    return max(0, min(99, int(final_percentage)))

with open('word_pool.json', 'r', encoding='utf-8') as f:
    word_data = json.load(f)

word_pools = word_data['themes']

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

                # --- NEW LOGIC STARTS HERE ---

                # 1. Fetch the target word and context based on the 2nd JSON approach
                theme_selected = response.content.lower()
                selected_item = random.choice(word_pools[theme_selected])
                target_word = selected_item['target']
                target_context = selected_item['context']
                target_phrase = f"{target_word}: {target_context}"
                target_embedding = model.encode(target_phrase)
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

                        # Calculate score using your placeholder function
                        score = get_nlp_score(guess_text, target_word, target_embedding)
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
                            fail_embed = discord.Embed(
                                title="Keep Guessing!",
                                description=(
                                    f"I interpreted your guess as `{guess_text}`, which gives a score of **{score}%**\n\n"
                                    f"**Attempts remaining:** {attempts}"
                                ),
                                color=discord.Color.orange()
                            )
                            fail_embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                            await message.channel.send(embed=fail_embed)

                        else:
                            lose_embed = discord.Embed(
                                title="Game Over",
                                description=(
                                    f"I interpreted your guess as `{guess_text}`, which gives a score of **{score}%**\n\n"
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