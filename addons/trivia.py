import json
import discord
from addon import Addon

SPAWN_INTERVAL = 7204
TIMEOUT_INTERVAL = 300
MONITOR_STATE = False

QUESTION_BANK = json.load(open('questions/trivia.json'))
IMAGE_BANK = json.load(open('images/geralt_trivia_images.json'))

TRIVIA_POINTS = 20

class Trivia(Addon):
    def __init__(self, *args, **kwargs):
        super().__init__(
                *args,
                spawn_interval=SPAWN_INTERVAL,
                timeout_interval=TIMEOUT_INTERVAL,
                activity_monitor_state=MONITOR_STATE,
                question_bank=QUESTION_BANK,
                image_bank=IMAGE_BANK
                )

    async def handle_spawn(self):
        await super().handle_spawn() 
        self.question = self.get_random_from_array(self.question_bank)
        image = self.get_random_from_array(self.image_bank['geralt_of_trivia'])

        embed = discord.Embed(
            title="Special Encounter: Geralt of Trivia",
            color=discord.Color.blue(),
            description=f"{self.question['question']}"
        )
        embed.set_image(url=image)
        embed.set_footer(text="Geralt demands satisfaction.  Answer the question.")

        self.message_embed = embed
        self.user_message = await self.channel.send(embed=embed)

    async def handle_success(self, message):
        self.message_embed.description = f"...and awards {message.author.mention} {TRIVIA_POINTS} points!"
        self.message_embed.set_footer(text="He is satisfied")
        image = self.get_random_from_array(self.image_bank['happy_geralt_of_trivia'])
        self.message_embed.set_image(url=image)
        await super().handle_success(message)
        await message.add_reaction("\U0001F389")

        #Update Leaderboard
        if not message.author.name in self.leaderboard:
            self.leaderboard.update({message.author.name: 0})
        self.leaderboard[message.author.name] += TRIVIA_POINTS
        if not message.author.name in self.safe_leaderboard:
            self.safe_leaderboard.update({message.author.name: 0})
        self.safe_leaderboard[message.author.name] += TRIVIA_POINTS

        #Clear response state
        self.awaiting_response = False


    async def handle_vanish(self):
        await super().handle_vanish(
                description="...fuck...",
                vanish_image_bank=self.image_bank['sad_geralt_of_trivia'],
                footer={'text': '...he is...unsatisfied'}
            )
