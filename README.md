# Bluesky Python Bot Tutorial

This folder contains a starter template for creating a bot on Bluesky.

## Set Up

1. Make a copy of the example `.env` file by running: `cp .env.example .env`. Set your username and password in `.env`. Use an App Password.
2. Create a new virtual environment with [`venv`](), [`poetry`](), or your personal favorite.

## Running the script 
1. You can run the script locally: `python3 main.py`. You should see a smiley emoji posted to your Bluesky account. 
2. Modify the script however you like to make this bot your own -- check out examples in `/examples`

## Deploying your bot
1. You can deploy a simple bot for free on [Fly.io]()
2. Install the `flyctl` CLI
   1. MacOS `brew install flyctl`
   2. Linux `curl -L https://fly.io/install.sh | sh`
   3. Windows `pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"`
3. Create an account with `fly auth signup` or login with `fly auth login`
4. Sign in with your GitHub
5. You can deploy a simple bot for free or low cost on a variety of platforms. For example, check out [Heroku](https://devcenter.heroku.com/articles/github-integration) or [Fly.io](https://fly.io/docs/reference/fly-launch/).
