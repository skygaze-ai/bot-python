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
BRANCH_FACTOR = 2
MAX_DEPTH = 1
QPS_est = 5

# Create a Bluesky client
client = Client("https://bsky.social")


def crawl() -> tuple[list, list]:
    # print estimate
    reqs_count = BRANCH_FACTOR ** (MAX_DEPTH - 1) + (BRANCH_FACTOR**MAX_DEPTH) * 5
    est_time = reqs_count / QPS_est / 60
    print(f"This crawl will make ~{reqs_count} reqs in {round(est_time, 2)} minutes")

    # get did for seed repo handle
    seed_did = client.resolve_handle(handle=SEED_REPO).did

    follows = []
    profiles_dict = {}

    current_round_dids = {seed_did}
    already_crawled_dids = set()
    next_round_dids = set()
    current_depth = 1

    # iterate
    while current_depth <= MAX_DEPTH:
        print(f"Starting round {current_depth}")

        for did in current_round_dids:
            # get follows
            try:
                actor_follows = client.get_follows(actor=did).follows

                sampled_follows = sample(
                    actor_follows, min(BRANCH_FACTOR, len(actor_follows))
                )
                for follow in sampled_follows:
                    # print(follow)
                    follows.append({"did": did, "subject_did": follow.did})
                    profiles_dict[follow.did] = {
                        "did": follow.did,
                        "handle": follow.handle,
                        "display_name": follow.display_name,
                        "description": follow.description,
                    }

                    # add new did to queue
                    if (
                        follow.did not in already_crawled_dids
                        and follow.did not in current_round_dids
                    ):
                        next_round_dids.add(follow.did)
            except Exception:
                actor_follows = []

        # update
        already_crawled_dids.update(current_round_dids)
        current_round_dids = next_round_dids
        next_round_dids = set()
        current_depth += 1

    profiles = list(profiles_dict.values())

    # get posts, reposts, likes, blocks
    posts = []
    reposts = []
    likes = []
    blocks = []

    for profile in profiles:
        did = profile["did"]
        try:
            posts += get_posts(did)
            reposts += get_reposts
            likes += get_likes(did)
            blocks += get_blocks(did)
        except Exception as e:
            print(e)
            pass

    return follows, profiles, posts, likes, blocks


def get_posts(did):
    try:
        return client.get_author_feed(actor=did, limit=50).feed
    except Exception as e:
        print(e)
        return []


def get_blocks(did):
    try:
        return client.app.bsky.graph.get_blocks(actor=did, limit=50).blocks
    except Exception as e:
        print(e)
        return []


def get_reposts(did):
    try:
        repost_records = client.com.atproto.repo.list_records(
            params={
                "repo": did,
                "collection": "app.bsky.feed.repost",
                "limit": 50,
            }
        ).records
        # transform them
        return repost_records
    except Exception as e:
        print(e)
        return []


def get_likes(did):
    try:
        like_records = client.com.atproto.repo.list_records(
            params={
                "repo": did,
                "collection": "app.bsky.feed.like",
                "limit": 50,
            }
        ).records
        # transform them
        return like_records
    except Exception as e:
        print(e)
        return []


def write_to_csv(follows, profiles, posts, likes, blocks):
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

    with open("data/sampled_posts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["uri", "cid", "author", "text"])

        for post in posts:
            writer.writerow([post.uri, post.cid, post.author, post.text])

    with open("data/sampled_likes.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["uri", "cid", "author", "liker"])

        for like in likes:
            writer.writerow([like.uri, like.cid, like.author, like.liker])

    with open("data/sampled_blocks.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["uri", "cid", "author", "reposter"])

        for block in blocks:
            writer.writerow([block.uri, block.cid, block.author, block.reposter])


def main() -> None:
    client.login(BLUESKY_USERNAME, BLUESKY_PASSWORD)
    follows, profiles, posts, likes, reposts = crawl()
    write_to_csv(follows, profiles, posts, likes, reposts)


if __name__ == "__main__":
    main()
