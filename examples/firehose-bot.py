import os

from atproto import (
    CAR,
    AtUri,
    Client,
    FirehoseSubscribeReposClient,
    firehose_models,
    models,
    parse_subscribe_repos_message,
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bluesky credentials
BLUESKY_USERNAME = os.getenv("BLUESKY_USERNAME")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

# Create a Bluesky client
client = Client("https://bsky.social")
firehose = FirehoseSubscribeReposClient()


def on_message_handler(message: firehose_models.MessageFrame) -> None:
    commit = parse_subscribe_repos_message(message)
    if not isinstance(
        commit, models.ComAtprotoSyncSubscribeRepos.Commit
    ) or not isinstance(commit.blocks, bytes):
        return

    car = CAR.from_bytes(commit.blocks)

    for op in commit.ops:
        uri = AtUri.from_str(f"at://{commit.repo}/{op.path}")

        if op.action == "create":
            if not op.cid:
                continue

            record = car.blocks.get(op.cid)
            if not record:
                continue

            record = {
                "uri": str(uri),
                "cid": str(op.cid),
                "author": commit.repo,
                **record,
            }

            if uri.collection == models.ids.AppBskyFeedPost:
                if "bluesky" in record["text"]:
                    client.send_post(text="Hello World from Python!")

            # Process other types of events:
            # elif uri.collection == models.ids.AppBskyFeedLike:
            #     print("Created like: ", record)
            # elif uri.collection == models.ids.AppBskyFeedRepost:
            #     print("Created repost: ", record)
            # elif uri.collection == models.ids.AppBskyGraphFollow:
            #     print("Created follow: ", record)

        if op.action == "delete":
            # Process delete(s)
            continue

        if op.action == "update":
            # Process update(s)
            continue


if __name__ == "__main__":
    client.login(BLUESKY_USERNAME, BLUESKY_PASSWORD)
    firehose.start(on_message_handler)
