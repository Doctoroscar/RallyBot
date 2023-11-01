FROM python:3.11.6

WORKDIR /srv/

RUN pip install discord

ADD bot.py /srv/
ADD addon.py /srv/
ADD images /srv/images
ADD questions /srv/questions
ADD addons /srv/addons
ADD leaderboard.json /srv/

CMD ["/usr/local/bin/python", "bot.py"]
