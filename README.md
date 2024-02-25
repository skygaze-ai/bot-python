# Bluesky Python Bot

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
5. Create a new virtual environment with [`venv`](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) or your favorite package manager.

Using venv:
`python3 -m venv .venv`
`source .venv/bin/activate`
`pip install -r requirements.txt`
When you're done: `deactivate`

## Building your bot

Modify the `main.py` script however you like to make this bot your own. The `/examples` director has `firehose-bot.py` and `cron-bot.py` - if you want your bot to respond to some kind of event live, you want firehose-bot. If instead you want to do something on a timer, use cron-bot. You might also want to do something that's kind of both (i.e. it listens to the websocket to index/aggregate data and then does something on a schedule, like say what the sentiment is for a given search term)

## Running your bot

You can run the script locally: `python3 main.py`. You should see a smiley emoji posted to your Bluesky account.

## Data

Data availability is a huge perk of atproto--data can be accessed by crawling the repos yourself, ingesting the firehose, querying bluesky's AppView, or querying someone else's service (like a labeler or feed generator).

For convenience we included samples of tables in `data/`. These are just samples, not the full tables. For the sake of example and so you can reason about the characteristics of the samples you got, we included `example/crawl.py` which is the script that generated the follows sample (and corresponding profiles). Feel free to generate your own sample by modifying `example/crawl.py`.

## Deploying your bot

For development, it's simplest to just run the bot locally (`python3 main.py`). When you want to deploy it for real, there are many free or low cost cloud hosting options like [Heroku](https://devcenter.heroku.com/articles/github-integration) or [Fly.io](https://fly.io/docs/reference/fly-launch/).
