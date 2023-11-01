import json
import discord
from addon import Addon

SPAWN_INTERVAL = 300
TIMEOUT_INTERVAL = 120
MONITOR_STATE = False

QUESTION_BANK = json.load(open('questions/riddles.json'))
IMAGE_BANK = json.load(open('images/riddle_images.json'))

RIDDLE_POINTS = 5

class Riddles(Addon):
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
        print("Loaded question: ", self.question)
        image = self.get_random_from_array(self.image_bank)

        embed = discord.Embed(
            title=f"{image['name']} approaches...",
            color=discord.Color.blue(),
            description=f"{self.question['riddle']}"
        )
        embed.set_image(url=image['url'])
        embed.set_footer(text="Answer their riddle!")

        self.message_embed = embed
        self.user_message = await self.channel.send(embed=embed)

    async def handle_success(self, message):
        self.message_embed.description = f"...and awards {message.author.mention} {RIDDLE_POINTS} points!"
        self.message_embed.set_footer(text="It is satisfied")
        await super().handle_success(message)
        await message.add_reaction("\U0001F389")

        #Update Leaderboard
        if not message.author.name in self.leaderboard:
            self.leaderboard.update({message.author.name: 0})
        self.leaderboard[message.author.name] += RIDDLE_POINTS

        #Clear response state
        self.awaiting_response = False

