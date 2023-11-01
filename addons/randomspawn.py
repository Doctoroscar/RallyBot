import random
import time
import discord
from addon import Addon

SPAWN_INTERVAL = 3833
TIMEOUT_INTERVAL = 10
MONITOR_STATE = False

QUESTION_BANK = []
IMAGE_BANK = []


class RandomSpawn(Addon):
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
        self.last_message_time = time.time()

        encounter = self.get_random_from_array(ENCOUNTERS)
        print(f"Invoke Random Encounter {encounter['name']}")
        self.leaderboard = encounter['function'](self.leaderboard)

        embed = discord.Embed(
                title=f"Random Encounter: {encounter['name']}",
                color=discord.Color.blue(),
                description=encounter['description']
        )
        embed.set_image(url=encounter['url'])
        embed.set_footer(text=encounter['footer'])

        self.awaiting_respose = False
        await self.channel.send(embed=embed)

    async def handle_success(self, message):
        self.awaiting_respose = False

    async def handle_vanish(self):
        self.awaiting_respose = False



def chaos_kitten(leaderboard):
    for user in leaderboard:
        leaderboard[user] += 1
    return leaderboard

def bob_the_dick(leaderboard):
    for user in leaderboard:
        if leaderboard[user] > 2:
            leaderboard[user] -= 1
    return leaderboard

def chaos_banana(leaderboard):
    for user in leaderboard:
        action_roll = random.randint(1,10)
        if action_roll <= 3:
            if leaderboard[user] > 2:
                leaderboard[user] -= 1
            else:
                leaderboard[user] += 1
        else:
            leaderboard[user] += random.randint(1, 2)
    return leaderboard

def betty_loot(leaderboard):
    sorted_leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)}
    coins = 5
    for user in sorted_leaderboard:
        if coins < 1:
            break
        leaderboard[user] += coins
        coins -= 1
    return leaderboard

def bob_the_enlightened(leaderboard):
    for user in leaderboard:
        heads_tails = random.randint(0, 1)
        if heads_tails == 1:
            leaderboard[user] += 1
    return leaderboard

def karl_sharx(leaderboard):
    top_sorted_leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)}
    low_sorted_leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1])}
    top_3 = [user for user in top_sorted_leaderboard][:3]
    bottom_3 = [user for user in low_sorted_leaderboard][:3]
    value_change = 5
    for user in top_3:
        if value_change < 1:
            continue
        elif user in bottom_3:
            continue
        elif leaderboard[user] >= 10:
            leaderboard[user] -= value_change
            value_change -= 2

    value_change = 5
    for user in bottom_3:
        if value_change < 1:
            continue
        elif user in top_3:
            continue
        leaderboard[user] += value_change
        value_change -= 2
    return leaderboard




ENCOUNTERS = [
    {
        "name": "Chaos Kitten",
        "url": "https://i.imgur.com/1L3bZO0.jpg",
        "function": chaos_kitten,
        "description": "...and gives everybody 1 point!",
        "footer": "good kitty"
    },
    {
        "name": "Bob the Dick",
        "url": "https://i.imgur.com/bFiX2Mr.jpg",
        "function": bob_the_dick,
        "description": "...and takes away up to 1 point!  Stop having fun!",
        "footer": "brought to you by Activision Blizzard"
    },
    {
        "name": "Chaos Banana",
        "url": "https://i.imgur.com/EQubOFR.jpg",
        "function": chaos_banana,
        "description": "...and randomly adjusts all scores by 1 or 2",
        "footer": "he has come for potassium"
    },
    {
        "name": "Betty Loot",
        "url": "https://i.imgur.com/qHJjkUb.jpg",
        "function": betty_loot,
        "description": "...and gives the commanding officers more loot!",
        "footer": "Yaarr, more booty for me first mateys!"
    },
    {
        "name": "Bob the Enlightened",
        "url": "https://i.imgur.com/9eEwgKV.jpg",
        "function": bob_the_enlightened,
        "description": "...and randomly gives back 1 point to random people",
        "footer": "vacation and surgery did him some good"
    },
    {
        "name": "Karl Sharx",
        "url": "https://i.imgur.com/kdhbBU1.jpg",
        "function": karl_sharx,
        "description": "...and brings about a wave of communism.\nSome wealth is redistributed...",
        "footer": "You have nothing to lose but your chains!"
    },
]
