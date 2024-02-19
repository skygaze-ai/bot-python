import os

from atproto import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bluesky credentials
BLUESKY_USERNAME = os.getenv("BLUESKY_USERNAME")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

# Create a Bluesky client
client = Client("https://bsky.social")


def main():
    client.login(BLUESKY_USERNAME, BLUESKY_PASSWORD)
    client.post("🙂")


if __name__ == "__main__":
    main()
