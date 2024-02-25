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
from openai import OpenAI

class FirehoseBot:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Bluesky credentials
        self.BLUESKY_USERNAME = os.getenv("BLUESKY_USERNAME")
        self.BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

        # Create a Bluesky client
        self.client = Client("https://bsky.social")
        self.firehose = FirehoseSubscribeReposClient()

        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.llm_client = OpenAI(api_key=OPENAI_API_KEY) 

    def translate_in_native_language(self, content, language):
        system_message = f"""\
        You are the translation expert. Translate {content} into {language}.\
        When translating, please keep as much nuance as possible. \
        Please do not change emojis, etc. as they are.\
        If there are any expressions that are too offensive, vulgar, or otherwise inappropriate, \
        please modify them to softer expressions.
        """

        messages = [{'role': 'system', 'content': system_message}, 
                    {"role": "user", "content": content}]

        response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages, 
            )

        print(response.choices[0].message.content)

    def process_operation(self, op: models.ComAtprotoSyncSubscribeRepos.RepoOp, car: CAR, commit: models.ComAtprotoSyncSubscribeRepos.Commit) -> None:
        uri = AtUri.from_str(f"at://{commit.repo}/{op.path}")

        if op.action == "create":
            if not op.cid:
                return

            record = car.blocks.get(op.cid)
            if not record:
                return

            record = {
                "uri": str(uri),
                "cid": str(op.cid),
                "author": commit.repo,
                **record,
            }
        

            if uri.collection == models.ids.AppBskyFeedPost:
                # This logs the text of every post off the firehose.
                # Just for fun :)
                # Delete before actually using
                if "translate-bot" in record["text"].lower():
                    print(record['text'])
                    print(self.translate_in_native_language(record['text'], 'japanese'))

            
                if "hack-bot" in record["text"]:
                    # get some info about the poster, their posts, and the thread they tagged the bot in
                    poster_posts = client.get_author_feed(
                        actor=record["author"], cursor=None, filter=None, limit=100
                    ).feed
                    poster_follows = client.get_follows(actor=record["author"]).follows
                    poster_profile = client.get_profile(actor=record["author"])
                    posts_in_thread = client.get_post_thread(uri=record["uri"])

                    # send a reply to the post
                    record_ref = {"uri": record["uri"], "cid": record["cid"]}
                    reply_ref = models.AppBskyFeedPost.ReplyRef(
                        parent=record_ref, root=record_ref
                    )
                    client.send_post(
                        reply_to=reply_ref,
                        text=f"Hey, {poster_profile.display_name}. You have {len(poster_posts)} posts and {len(poster_follows)} follows. Your bio is: {poster_profile.description}. There are {len(posts_in_thread)} posts in the thread.",
                    )

            # elif uri.collection == models.ids.AppBskyFeedLike:
            #     print("Created like: ", record)
            # elif uri.collection == models.ids.AppBskyFeedRepost:
            #     print("Created repost: ", record)
            # elif uri.collection == models.ids.AppBskyGraphFollow:
            #     print("Created follow: ", record)

        if op.action == "delete":
            # Process delete(s)
            return

        if op.action == "update":
            # Process update(s)
            return

        return

    def on_message_handler(self, message: firehose_models.MessageFrame) -> None:
        commit = parse_subscribe_repos_message(message)
        if not isinstance(
            commit, models.ComAtprotoSyncSubscribeRepos.Commit
        ) or not isinstance(commit.blocks, bytes):
            return

        car = CAR.from_bytes(commit.blocks)

        for op in commit.ops:
            self.process_operation(op, car, commit)

    def start(self):
        self.client.login(self.BLUESKY_USERNAME, self.BLUESKY_PASSWORD)
        print("🤖 Bot is listening")
        self.firehose.start(self.on_message_handler)

    def get_firehose(self):
        return self.firehose