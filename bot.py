import os
import discord
from discord.ext import tasks
import random
import json
import time
import asyncio

from addons.riddles import Riddles 
from addons.trivia import Trivia
from addons.turkey_trivia import TurkeyTrivia
from addons.mariah_carrion import MariahCarrion
from addons.mariah_carry import MariahCarry
from addons.randomspawn import RandomSpawn
from addons.yulon import YuLon
from addons.anduin import Anduin
from addons.xalax import Xalax

BACKGROUND_TIMER_SECONDS = 30
ENABLED_ADDONS = [
        Xalax,
        Trivia,
        ]
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']

LEADERBOARD_FILE='leaderboard.json'
TRIVIA_LEADERBOARD_FILE = 'trivia_leaderboard.json'
LEADERBOARD_LENGTH=10
DUEL_POINT_MIN = 1
DUEL_POINT_MAX = 3
DUEL_WAIT_TIME_MINUTES = 2
DUEL_FILE = 'images/duels.json'
DUEL_DATA = json.load(open(DUEL_FILE))

class RallyBot(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        self.channel = self.get_channel(int(CHANNEL_ID))
        print(self.channel)
        self.channel_last_message_time = time.time()

        self.leaderboard = self.load_leaderboard(LEADERBOARD_FILE)
        self.trivia_leaderboard = self.load_leaderboard(TRIVIA_LEADERBOARD_FILE)

        self.duel_in_progress = False

        self.addons = [
                addon(self.channel, self.leaderboard, self.trivia_leaderboard) for addon in ENABLED_ADDONS
        ]

        #Default them to assume they've already sent so that we dont get a thundering herd
        for addon in self.addons:
            addon.last_message_time = time.time()

        self.background_timer.start()

        print('-----------')
        print("-- Ready --")
        print('-----------')



    def save_leaderboard(self):
        with open(LEADERBOARD_FILE, 'w') as f:
            f.write(json.dumps(self.leaderboard))
        with open(TRIVIA_LEADERBOARD_FILE, 'w') as f:
            f.write(json.dumps(self.trivia_leaderboard))
        print("Successfully saved leaderboards")


    def load_leaderboard(self, leaderboard_file):
        try:
            with open(leaderboard_file) as f:
                return json.load(f)
            print("Successfully loaded saved leaderboard")
        except Exception as e:
            print("Failed to load leaderboard, starting blank")
            return {}


    async def print_leaderboard(self, channel, leaderboard, score_type="Score"):
        embed = discord.Embed(
            title="Leaderboard: Top 10",
            color=discord.Color.yellow(),
        )
        names = []
        scores = []
        sorted_leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)}
        count = 0
        for user in sorted_leaderboard:
            if count > LEADERBOARD_LENGTH:
                break
            names.append(user)
            scores.append(str(leaderboard[user]))
            count += 1

        embed.add_field(
            name="Handle",
            value='\n'.join(names)
        )
        embed.add_field(
            name=score_type,
            value='\n'.join(scores)
        )
        await channel.send(embed=embed)

    async def print_score(self, channel, author):
        score = self.leaderboard.get(author, 0)
        embed = discord.Embed(
            title=f"{author}'s score",
            color=discord.Color.yellow(),
            description=f"{score} points"
        )
        await channel.send(embed=embed)

    async def on_message(self, message):
        self.channel_last_message_time = time.time()
        if int(message.channel.id) != int(CHANNEL_ID):
            pass #ignore messages from other channels

        elif message.content.lower() == 'leaderboard':
            await self.print_leaderboard(message.channel, self.leaderboard)
            await self.print_leaderboard(message.channel, self.trivia_leaderboard, score_type="Questions Answered")

        elif message.content.lower() == 'score':
            await self.print_score(message.channel, message.author.name)

        elif message.content.lower().startswith('duel '):
            if self.duel_in_progress:
                if message.mentions:
                    await message.channel.send("Duel in progress...wait for it to finish first")
            else:
                print("Duel: ", message.author.name, message.mentions[0].name)
                #Second make sure that person has points
                if message.author.name == message.mentions[0].name:
                    await message.channel.send(f"{message.author.name} commits suicide by slappers!")
                elif message.author.name not in self.leaderboard:
                    await message.channel.send(f"{message.author.name} cannot duel until they have points!")
                elif message.mentions[0].name not in self.leaderboard:
                    await message.channel.send(f"{message.mentions[0].name} cannot duel until they have points!")
                elif self.leaderboard[message.author.name] < 1:
                    await message.channel.send(f"{message.author.name} needs at least 1 point to duel!")
                elif self.leaderboard[message.mentions[0].name] < 1:
                    await message.channel.send(f"{message.mentions[0].name} needs at least 1 point to duel!")
                else:
                    message_end = message.content.split(' ')[-1].strip()
                    try:
                        int(message_end)
                        duel_point_max = int(message_end)
                    except ValueError:
                        duel_point_max = DUEL_POINT_MAX
                    await self.handle_duel(message, message.author.name, message.mentions[0].name, duel_point_max)

        else:
            for addon in self.addons:
                await addon.process_message(message)


    @tasks.loop(seconds=BACKGROUND_TIMER_SECONDS)
    async def background_timer(self):
        print("Invoke process loop")
        for addon in self.addons:
            if addon.is_ready(channel_last_message_time=self.channel_last_message_time):
                print("Addon is ready to spawn")
                await addon.handle_spawn()
            elif addon.is_timed_out():
                print("Addon has timed out")
                await addon.handle_vanish()

        self.save_leaderboard()


    async def handle_duel(self, message, dueler1, dueler2, duel_point_max=DUEL_POINT_MAX):

        def get_random_image(array):
            number = random.randint(0, len(array)-1)
            return array[number]

        self.duel_in_progress = True

        # Figure out how many points we can bet, between min and max
        dueler1_max = min(self.leaderboard[dueler1], duel_point_max)
        dueler2_max = min(self.leaderboard[dueler2], duel_point_max)

        duel_point_max = min(dueler1_max, dueler2_max)
        print(f"Duel will commence over 1-{duel_point_max} points!")

        # Get a random value between min and max (inclusive)
        duel_point_stake = random.randint(1, duel_point_max)
        print(f"Duel over {duel_point_stake} points!")

        # Enter a duel message
        embed = discord.Embed(
            title="A Duel has Begun!",
            color=discord.Color.red(),
            description=f"{dueler1} vs {dueler2}"
        )
        embed.add_field(
            name="Duel Rules",
            value=f"RNG Rolls, winner takes {duel_point_stake} points from loser"
        )
        embed.add_field(
            name="Community Participation",
            value=f"Cast a vote to stake 1 point to gain or lose!\n- Guess right, gain 1.\n- Guess wrong, lose 1.\n\n:one: for {dueler1}\n:two: for {dueler2}"
        )

        embed.set_image(url=get_random_image(DUEL_DATA['duel_challenge']))

        embed.set_footer(text=f"Duel will commence in {DUEL_WAIT_TIME_MINUTES} minutes")

        duel_message = await message.channel.send(embed=embed) 

        # Sleep for a DUEL countdown timer
        #await asyncio.sleep(DUEL_WAIT_TIME_MINUTES*60)
        await duel_message.add_reaction("1️⃣")
        await duel_message.add_reaction("2️⃣")

        await asyncio.sleep(DUEL_WAIT_TIME_MINUTES*60)

        pending_msg = await message.channel.fetch_message(duel_message.id)
        reactions = pending_msg.reactions

        dueler1_voters = []
        dueler2_voters = []
        d1_skip = False
        d2_skip = False
        async for item in reactions[0].users():
            if not d1_skip:
                d1_skip = True
                continue
            dueler1_voters.append(item.name)
        async for item in reactions[1].users():
            if not d2_skip:
                d2_skip = True
                continue
            dueler2_voters.append(item.name)

        # Accrew reactions for bets

        # Roll for winner (roll out of 100)
        dueler1_roll = random.randint(1, 100)
        dueler2_roll = random.randint(1, 100)

        # Winner gains points, loser loses points

        # Case 1, tie
        result_embed = discord.Embed(
            title=f"Duel Results:",
            color=discord.Color.red(),
            description=f"{dueler1} vs {dueler2}"
        )
        result_embed.add_field(
            name=f"{dueler1}",
            value=f"Rolls {dueler1_roll}"
        )
        result_embed.add_field(
            name=f"{dueler2}",
            value=f"Rolls {dueler2_roll}"
        )

        if dueler1_roll == 69 or dueler2_roll == 69:
            if dueler1_roll == dueler2_roll:
                result_embed.title = f"Duel Result: DOUBLE 69s!"
            elif dueler1_roll == 69:
                result_embed.title = f"Duel Result: {dueler1} rolled a 69!"
            else:
                result_embed.title = f"Duel Result: {dueler2} rolled a 69!"

            result_embed.description = "69 Party!"
            self.leaderboard[dueler1] += 9
            self.leaderboard[dueler2] += 9

            result_embed.add_field(
                name="Point Distrubtion",
                value=f"{dueler1} and {dueler2} receive 9 points!\nCommunity gains 6 points each!"
            )

            unique_voters = list(set(dueler1_voters + dueler2_voters))
            for dueler in unique_voters:
                if dueler in self.leaderboard:
                    if self.leaderboard[dueler] >= 1:
                        self.leaderboard[dueler] += 6

            result_embed.add_field(
                name="Community Vote Winners",
                value="\n".join(unique_voters)
            )
            result_embed.add_field(
                name="Community Vote Losers",
                value="Nobody loses when there's a 69!"
            )
            result_embed.set_image(url=get_random_image(DUEL_DATA['dueler_69']))



        elif dueler1_roll == dueler2_roll:
            result_embed.title = "Duel Result: TIE!"
            result_embed.description=f"{dueler1} and {dueler2} both misfired..."
            self.leaderboard[dueler1] += 1
            self.leaderboard[dueler2] += 1

            result_embed.add_field(
                name="Point Distrubtion",
                value="F$ck it! Both duelers gain a point!"
            )

            result_embed.add_field(
                name="Community Votes",
                value="TIE! All points refunded!"
            )
            result_embed.set_image(url=get_random_image(DUEL_DATA['duel_tie']))

            self.leaderboard[dueler1] += 1
            self.leaderboard[dueler2] += 1
            
            #skip emoji points
            #Set imbed to have a tie image
        elif dueler1_roll > dueler2_roll:
            result_embed.title = f"Duel Result: {dueler1} wins!"
            result_embed.description = f"{dueler1} has killed {dueler2}"
            self.leaderboard[dueler1] += duel_point_stake
            self.leaderboard[dueler2] -= duel_point_stake

            result_embed.add_field(
                name="Point Distrubtion",
                value=f"{dueler1} has taken {duel_point_stake} from {dueler2}"
            )

            for dueler in dueler1_voters:
                if dueler in self.leaderboard:
                    if self.leaderboard[dueler] >= 1:
                        self.leaderboard[dueler] += 1
            for dueler in dueler2_voters:
                if dueler in self.leaderboard:
                    if self.leaderboard[dueler] >= 1:
                        self.leaderboard[dueler] -= 1

            result_embed.add_field(
                name="Community Vote Winners",
                value="\n".join(dueler1_voters)
            )
            result_embed.add_field(
                name="Community Vote Losers",
                value="\n".join(dueler2_voters)
            )
            result_embed.set_image(url=get_random_image(DUEL_DATA['dueler_1_wins']))

        elif dueler2_roll > dueler1_roll:
            result_embed.title = f"Duel Result: {dueler2} wins!"
            result_embed.description = f"{dueler2} has killed {dueler1}"
            self.leaderboard[dueler2] += duel_point_stake
            self.leaderboard[dueler1] -= duel_point_stake

            result_embed.add_field(
                name="Point Distrubtion",
                value=f"{dueler2} has taken {duel_point_stake} from {dueler1}"
            )

            for dueler in dueler2_voters:
                if dueler in self.leaderboard:
                    if self.leaderboard[dueler] >= 1:
                        self.leaderboard[dueler] += 1
            for dueler in dueler1_voters:
                if dueler in self.leaderboard:
                    if self.leaderboard[dueler] >= 1:
                        self.leaderboard[dueler] -= 1

            result_embed.add_field(
                name="Community Vote Winners",
                value="\n".join(dueler2_voters)
            )
            result_embed.add_field(
                name="Community Vote Losers",
                value="\n".join(dueler1_voters)
            )
            result_embed.set_image(url=get_random_image(DUEL_DATA['dueler_2_wins']))

        # Edit the result message
        self.duel_in_progress = False
        await duel_message.edit(embed=result_embed)


intents = discord.Intents.default()
intents.message_content = True

client = RallyBot(intents=intents)
client.run(DISCORD_TOKEN)
