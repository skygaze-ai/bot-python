import os
import csv

from atproto import Client
from dotenv import load_dotenv
from random import sample

# Load environment variables
load_dotenv()

# Bluesky credentials
BLUESKY_USERNAME = os.getenv("BLUESKY_USERNAME")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

SEED_REPO = "cooperedmunds.bsky.social"
BRANCH_FACTOR = 15
MAX_DEPTH = 4
QPS = 5

# Create a Bluesky client
client = Client("https://bsky.social")


def crawl() -> tuple[list, list]:
    # print estimate
    est_follows_count = BRANCH_FACTOR**MAX_DEPTH
    est_time = (BRANCH_FACTOR ** (MAX_DEPTH - 1) / QPS) / 60
    print(
        f"This crawl will get <{est_follows_count} follows in {round(est_time, 2)} minutes"
    )

    # get did for seed repo handle
    seed_did = client.resolve_handle(handle=SEED_REPO).did

    all_follows = []
    profiles = {}

    current_round_of_dids = {seed_did}
    crawled_dids = set()
    queued_dids = set()
    depth = 1

    # iterate
    while depth <= MAX_DEPTH:
        print(f"Starting round {depth}")

        for did in current_round_of_dids:
            # get follows
            try:
                follows = client.get_follows(actor=did).follows

                sampled_follows = sample(follows, min(BRANCH_FACTOR, len(follows)))
                for follow in sampled_follows:
                    # print(follow)
                    all_follows.append({"did": did, "subject_did": follow.did})
                    profiles[follow.did] = {
                        "did": follow.did,
                        "handle": follow.handle,
                        "display_name": follow.display_name,
                        "description": follow.description,
                    }

                    # add new did to queue
                    if (
                        follow.did not in crawled_dids
                        and follow.did not in current_round_of_dids
                    ):
                        queued_dids.add(follow.did)
            except Exception:
                follows = []

        # update
        crawled_dids.update(current_round_of_dids)
        current_round_of_dids = queued_dids
        queued_dids = set()
        depth += 1

    return all_follows, list(profiles.values())


def write_to_csv(follows, profiles):
    # write to csv
    with open("data/sampled_follows.csv", "w") as f:
        f.write("did,subject_did\n")
        for follow in follows:
            f.write(f"{follow['did']},{follow['subject_did']}\n")

    with open("data/sampled_profiles.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["did", "handle", "display_name", "description"])

        for profile in profiles:
            writer.writerow(
                [
                    profile["did"],
                    profile["handle"],
                    profile["display_name"],
                    profile["description"],
                ]
            )


def main() -> None:
    client.login(BLUESKY_USERNAME, BLUESKY_PASSWORD)
    follows, profiles = crawl()
    write_to_csv(follows, profiles)


if __name__ == "__main__":
    main()
