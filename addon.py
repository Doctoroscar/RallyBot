import time
import random
import discord

ACTIVITY_INTERVAL = 300
DEFAULT_SPAWN_INTERVAL_SECONDS = 3600 #1 hour
DEFAULT_TIMEOUT_INTERVAL_SECONDS = 120
DEFAULT_ACTIVITY_MONITOR_STATE = False
DEFAULT_DESCRIPTION = '...but vanished into thin air!'
NEGATIVE_STRING = "129r0fhjnedi89v-<F7>201cak"

class Addon(object):
    def __init__(self, channel, leaderboard, *args, **kwargs):
        self.spawn_interval = kwargs.get('spawn_interval', DEFAULT_SPAWN_INTERVAL_SECONDS)
        self.timeout_interval = kwargs.get('timeout_interval', DEFAULT_TIMEOUT_INTERVAL_SECONDS)
        self.activity_monitor_state = kwargs.get('activity_monitor_state', DEFAULT_ACTIVITY_MONITOR_STATE)
        self.last_message_time = time.time() #Don't start right away or we'll spam everything
        self.channel = channel

        self.leaderboard = leaderboard

        self.awaiting_response = False
        self.user_message = None  #Message from a user in discord that triggers a response
        self.message_embed = None #Use discord embed for best experience
        self.question = None

        self.question_bank = kwargs.get('question_bank', {})
        self.image_bank = kwargs.get('image_bank', {})
        self.fail_image_bank = kwargs.get('fail_image_bank', {})
        self.success_image_bank = kwargs.get('success_image_bank', {})

    def is_ready(self, *args, **kwargs):
        if self.awaiting_response:
            return False

           
        print(self.__class__, "last active message at",  kwargs.get('channel_last_message_time'))
        if self.activity_monitor_state and (time.time() - kwargs.get('channel_last_message_time') > ACTIVITY_INTERVAL):
            print("Activity on, activity threshhold exceeded")
            return True
        else:
            return time.time() - self.last_message_time > self.spawn_interval

    def is_timed_out(self):
        if self.awaiting_response:
            if time.time() - self.last_message_time > self.timeout_interval:
                return True
        return False

    def get_random_from_array(self, array):
        number = random.randint(0, len(array) - 1)
        return array[number]
    
    async def handle_vanish(self, 
                    description=DEFAULT_DESCRIPTION,
                    vanish_image_bank=[],
                            footer={"text": "It leaves...unsatisfied"}
                ):
        self.message_embed.description = description
        if footer:
            self.message_embed.set_footer(**footer)
        if vanish_image_bank:
            self.message_embed.set_image(url=self.get_random_from_array(vanish_image_bank))
        self.awaiting_response = False
        await self.user_message.edit(embed=self.message_embed)

    async def handle_success(self, message):
        await self.user_message.edit(embed=self.message_embed)

    async def handle_spawn(self):
        self.last_message_time = time.time()
        self.awaiting_response = True


    async def process_message(self, message):
        if self.awaiting_response and self.question:
            if message.content.lower() in self.question['answers'] or message.content.lower().replace('a ', '') in self.question['answers']:
                await self.handle_success(message)
            #Something fun
            elif message.content.lower() in self.question.get("sarcastic-answers", [NEGATIVE_STRING]):
                await message.channel.send(f"{message.author.mention}" + self.question['sarcastic-response'])
