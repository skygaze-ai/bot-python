import csv
import os
from random import sample

from atproto import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bluesky credentials
BLUESKY_USERNAME = os.getenv("BLUESKY_USERNAME")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

SEED_REPO = "cooperedmunds.bsky.social"
BRANCH_FACTOR = 50
MAX_DEPTH = 2
QPS_est = 5

# Create a Bluesky client
client = Client("https://bsky.social")


def crawl() -> tuple[list, list, list, list, list, list]:
    # print estimate
    reqs_count = BRANCH_FACTOR ** (MAX_DEPTH - 1) + (BRANCH_FACTOR**MAX_DEPTH) * 6
    est_time = reqs_count / QPS_est / 60
    print(f"This crawl will make ~{reqs_count} reqs in {round(est_time, 2)} minutes")

    # get did for seed repo handle
    seed_did = client.resolve_handle(handle=SEED_REPO).did

    follows = []

    current_round_dids = {seed_did}
    already_crawled_dids = set()
    next_round_dids = set()
    current_depth = 1

    universe_of_dids = {seed_did}
    # iterate
    while current_depth <= MAX_DEPTH:
        print(f"Starting round {current_depth}")

        for did in current_round_dids:
            # get follows
            try:
                actor_follows = get_follows(did)
                print(did, 'follows', len(actor_follows))

                for follow in actor_follows:
                    subject_did = follow["subject"]

                    follows.append(follow)
                    universe_of_dids.add(subject_did)

                    # add new did to queue
                    if (
                        subject_did not in already_crawled_dids
                        and subject_did not in current_round_dids
                    ):
                        next_round_dids.add(subject_did)
            except Exception as e:
                print(e.content.message)
                actor_follows = []

        # update
        already_crawled_dids.update(current_round_dids)
        current_round_dids = next_round_dids
        next_round_dids = set()
        current_depth += 1

    # get profiles, posts, reposts, likes, blocks
    profiles = []
    posts = []
    reposts = []
    likes = []
    blocks = []

    for did in universe_of_dids:
        try:
            profiles += get_profile(did)
            posts += get_posts(did)
            reposts += [
                repost
                for repost in get_reposts(did)
                if did_from_uri(repost["subject_uri"]) in universe_of_dids
            ]
            likes += [
                like
                for like in get_likes(did)
                if did_from_uri(like["subject_uri"]) in universe_of_dids
            ]
            blocks += [
                block
                for block in get_blocks(did)
                if follow["subject"] in universe_of_dids
            ]
            if did not in already_crawled_dids:
                follows += [
                    follow
                    for follow in get_follows(did)
                    if follow["subject"] in universe_of_dids
                ]
        except Exception as e:
            print(e)
            pass

    return follows, profiles, posts, reposts, likes, blocks


def did_from_uri(uri):
    parts = uri.split("at://")

    # Further split the second part at "/app.bsky" and take the first portion
    if len(parts) > 1:
        return parts[1].split("/app.bsky")[0]
    else:
        return ""


def get_follows(did):
    try:
        follow_records = client.com.atproto.repo.list_records(
            params={
                "repo": did,
                "collection": "app.bsky.graph.follow",
                "limit": 50,
            }
        ).records
        follows = []
        for record in follow_records:
            follows.append(
                {
                    "uri": record.uri,
                    "did": did,
                    "subject": record.value.subject,
                    "created_at": record.value.created_at,
                }
            )
        sampled_follows = sample(follows, min(BRANCH_FACTOR, len(follows)))
        return sampled_follows
    except Exception as e:
        print(e)
        return []


def get_profile(did):
    try:
        profile = client.app.bsky.actor.get_profile({"actor": did})
        return [
            {
                "did": profile.did,
                "handle": profile.handle,
                "display_name": profile.display_name,
                "description": profile.description,
                "followers_count": profile.followers_count,
                "follows_count": profile.follows_count,
                "posts_count": profile.posts_count,
            }
        ]
    except Exception as e:
        print(e)
        return []


def get_posts(did):
    try:
        post_objects = client.get_author_feed(actor=did, limit=50).feed
        posts = []
        for post in post_objects:
            record = post.post.record
            subject = getattr(record, "subject", None)
            reply = getattr(record, "reply", None)

            posts.append(
                {
                    "uri": post.post.uri,
                    "did": post.post.author.did,
                    "created_at": record.created_at,
                    "root_uri": reply.root.uri if reply else None,
                    "parent_uri": reply.parent.uri if reply else None,
                    "subject_uri": subject.uri if subject else None,
                    "card_link": getattr(record, "external_uri", None),
                    "like_count": post.post.like_count,
                    "reply_count": post.post.reply_count,
                    "repost_count": post.post.repost_count,
                    "labels": post.post.author.labels,
                    "text": record.text,
                    # "images": record.embed. if record.embed else [],
                }
            )
        return posts
    except Exception as e:
        print("error in get_posts", e)
        return []


def get_blocks(did):
    try:
        block_records = client.com.atproto.repo.list_records(
            params={
                "repo": did,
                "collection": "app.bsky.graph.block",
                "limit": 50,
            }
        ).records
        blocks = []
        for record in block_records:
            blocks.append(
                {
                    "uri": record.uri,
                    "did": did,
                    "subject": record.value.subject,
                    "created_at": record.value.created_at,
                }
            )
        return blocks
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
        reposts = []
        for record in repost_records:
            reposts.append(
                {
                    "uri": record.uri,
                    "did": did,
                    "subject_uri": record.value.subject.uri,
                    "created_at": record.value.created_at,
                }
            )
        return reposts
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
        likes = []
        for record in like_records:
            likes.append(
                {
                    "uri": record.uri,
                    "did": did,
                    "subject_uri": record.value.subject.uri,
                    "created_at": record.value.created_at,
                }
            )
        return likes
    except Exception as e:
        print(e)
        return []


def write_to_csv(follows, profiles, posts, reposts, likes, blocks):
    # write to csv
    with open("data/sampled_follows.csv", "w") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["uri", "did", "subject", "created_at"])

        for follow in follows:
            try:
                writer.writerow(
                    [
                        follow["uri"],
                        follow["did"],
                        follow["subject"],
                        follow["created_at"],
                    ]
                )
            except Exception as e:
                print("error writing follow", e)

    with open("data/sampled_profiles.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(
            [
                "did",
                "handle",
                "display_name",
                "description",
                "followers_count",
                "follows_count",
                "posts_count",
            ]
        )

        for profile in profiles:
            try:
                writer.writerow(
                    [
                        profile["did"],
                        profile["handle"],
                        profile["display_name"],
                        profile["description"],
                        profile["followers_count"],
                        profile["follows_count"],
                        profile["posts_count"],
                    ]
                )
            except Exception as e:
                print("error writing profile", e)

    with open("data/sampled_posts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(
            [
                "uri",
                "did",
                "created_at",
                "root_uri",
                "parent_uri",
                "subject_uri",
                "card_link",
                "like_count",
                "reply_count",
                "repost_count",
                "labels",
                "text",
            ]
        )

        for post in posts:
            try:
                writer.writerow(
                    [
                        post["uri"],
                        post["did"],
                        post["created_at"],
                        post["root_uri"],
                        post["parent_uri"],
                        post["subject_uri"],
                        post["card_link"],
                        post["like_count"],
                        post["reply_count"],
                        post["repost_count"],
                        post["labels"],
                        post["text"],
                    ]
                )
            except Exception as e:
                print("error writing post", e)

    with open("data/sampled_reposts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["uri", "did", "subject_uri", "created_at"])

        for repost in reposts:
            try:
                writer.writerow(
                    [
                        repost["uri"],
                        repost["did"],
                        repost["subject_uri"],
                        repost["created_at"],
                    ]
                )
            except Exception as e:
                print("error writing repost", e)

    with open("data/sampled_likes.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["uri", "did", "subject_uri", "created_at"])

        for like in likes:
            try:
                writer.writerow(
                    [
                        like["uri"],
                        like["did"],
                        like["subject_uri"],
                        like["created_at"],
                    ]
                )
            except Exception as e:
                print("error writing like", e)

    with open("data/sampled_blocks.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["uri", "did", "subject", "created_at"])

        for block in blocks:
            try:
                writer.writerow(
                    [
                        block["uri"],
                        block["did"],
                        block["subject"],
                        block["created_at"],
                    ]
                )
            except Exception as e:
                print("error writing block", e)


def main() -> None:
    client.login(BLUESKY_USERNAME, BLUESKY_PASSWORD)
    follows, profiles, posts, reposts, likes, blocks = crawl()
    write_to_csv(follows, profiles, posts, reposts, likes, blocks)


if __name__ == "__main__":
    main()
