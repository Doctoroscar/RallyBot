import random
import time
import discord
from addon import Addon

SPAWN_INTERVAL = 2233
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

def george_w_butcher(leaderboard):
    sorted_leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)}
    coins = 5
    for user in sorted_leaderboard:
        if coins < 1:
            break
        leaderboard[user] += coins
        coins -= 1
    return leaderboard


def broccoli_obama(leaderboard):
    sorted_leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1])}
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


def james_devourer_of_worlds(leaderboard):
    top_sorted_leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)}
    sorted_users = [k for k in top_sorted_leaderboard]
    for user in sorted_users[3:-3]:
        leaderboard[user] += 5
    return leaderboard


def broseph_stalin(leaderboard):
    top_sorted_leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)}
    sorted_users = [k for k in top_sorted_leaderboard]
    points_diff = int((leaderboard[sorted_users[0]] - leaderboard[sorted_users[1]])/2)
    leaderboard[sorted_users[0]] -= points_diff
    while points_diff > 0:
        for user in sorted_users[3:]:
            leaderboard[user] += 1
            points_diff -= 1
    new_top_sorted_leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)}
    return leaderboard

def vladmir_lenin(leaderboard):
    top_sorted_leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)}
    sorted_users = [k for k in top_sorted_leaderboard]
    points_diff = int((leaderboard[sorted_users[0]] - leaderboard[sorted_users[1]])/4) #Quarter
    for user in sorted_users[1:]:
        leaderboard[user] += points_diff
    return leaderboard

def justin_trubro(leaderboard):
    bottom_sorted_leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=False)}
    sorted_users = [k for k in bottom_sorted_leaderboard]
    rand_number = random.randint(1, 3)
    user = sorted_users[rand_number]
    leaderboard[user] += 35
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
    {
        "name": "Broccoli Obama",
        "url": "https://i.imgur.com/yOCf2QX.jpg",
        "function": broccoli_obama,
        "description": "...and brings a green deal.\nThe bottom of the ladder receives benefits...",
        "footer": "We don't need no meat!"
    },
    {
        "name": "James, Devourer of Worlds",
        "url": "https://i.imgur.com/BXu3pTd.png",
        "function": james_devourer_of_worlds,
        "description": "...and brings 5 points to those in the middle",
        "footer": "everything, everything will be just fine"
    },
    {
        "name": "Broseph Stall-in",
        "url": "https://i.imgur.com/OT37AKV.jpg",
        "function": broseph_stalin,
        "description": "...and cuts the capitalist's lead",
        "footer": "History shows that there are no invincible armies"
    },
    {
        "name": "Vladmir \"Ima-John\" Lenin",
        "url": "https://i.imgur.com/7vq6mAd.jpg",
        "function": vladmir_lenin,
        "description": "...and hands out dueling points! Rise up!",
        "footer": "Imagine all the people...given an AK"
    },
    {
        "name": "Justin TruBro",
        "url": "https://i.imgur.com/8takMve.jpg",
        "function": justin_trubro,
        "description": "...and uplifts a random loser",
        "footer": "Universal healthcare, one person at a time"
    },
    {
        "name": "George W Butcher",
        "url": "https://i.imgur.com/0a2oif8.jpg",
        "function": george_w_butcher,
        "description": "...and brings a red deal.\nThe top of the ladder receives benefits...",
        "footer": "You need protein!"
    },
]
