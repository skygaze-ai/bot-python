# Bluesky Python Bot Tutorial

This repository contains a starter template for creating a Python bot on Bluesky.

💡 Some possible bots:

- Listens to the firehose and replies to every post that contains "tldr-bot" with a summary of the thread it was tagged in (see `examples/firehose-bot.py`)
- Posts a random image every hour (see `examples/cron-bot.py`)
- Listens to the firehose to see what topics are trending, posts a list of trending topics every 5 minutes

## Set Up

1. Create a new Bluesky account for your bot on the app or website (https://bsky.app)
2. Generate an App Password for your bot account in [settings](https://bsky.app/settings/app-passwords) (this is just to protect your real password)
3. Make a copy of the example `.env` file by running: `cp .env.example .env`
4. Set your bot's username and app password in `.env`
5. Create a new virtual environment with [`venv`](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) or your personal favorite.

## Running the script

1. You can run the script locally: `python3 main.py`. You should see a smiley emoji posted to your Bluesky account.
2. Modify the script however you like to make this bot your own. The `/examples` director has `firehose-bot.py` and `cron-bot.py` - if you want your bot to respond to some kind of event live, you want firehose-bot. If instead you want to do something on a timer, use cron-bot. You might also want to do something that's kind of both (i.e. it listens to the websocket to index/aggregate data and then does something on a schedule, like say what the sentiment is for a given search term)

## Deploying your bot

For demos, it's simplest to keep your computer running and just run the bot locally (`python3 main.py`). When you want to deploy it for real, there are many free or low cost cloud hosting options. For example, check out [Heroku](https://devcenter.heroku.com/articles/github-integration) or [Fly.io](https://fly.io/docs/reference/fly-launch/).
