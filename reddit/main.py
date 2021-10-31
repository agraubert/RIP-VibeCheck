import asyncio
import asyncpraw
from aiostream import stream
from datetime import datetime
from abc import ABC, abstractmethod
import csv
from contextlib import ExitStack

TIMESTAMP_FORMAT = "%m/%d/%Y - %H:%M:%S"

async def lazy_fetch_atribute(obj, attribute):
    try:
        return getattr(obj, attribute)
    except AttributeError:
        await obj.load()
        return getattr(obj, attribute)

class AbstractOutputStream(ABC):

    async def consume(self, comment):
        self.write(await self.extract_data(comment))

    @abstractmethod
    def write(self, data):
        pass

    async def extract_data(self, comment):
        author = comment.author
        await author.load()
        sub = comment.subreddit
        await sub.load()
        post = comment.submission
        await post.load()
        parent_id = comment.parent_id
        is_top_level = parent_id.startswith('t3_')
        now = datetime.now().strftime(TIMESTAMP_FORMAT)
        return {
            'comment_id': comment.id,
            'permalink': comment.permalink,
            'created_time': datetime.fromtimestamp(comment.created).strftime(TIMESTAMP_FORMAT),
            'author_username': author.name,
            'author_id': author.id,
            'comment_text': comment.body,
            'comment_score': comment.score,
            'comment_score_last_updated': now,
            'subreddit_name': sub.display_name,
            'subreddit_id': sub.id,
            'post_permalink': post.permalink,
            'post_title': post.title,
            'post_id': post.id,
            'post_score': post.score,
            'post_score_last_updated': now,
            'is_top_level': is_top_level,
            'parent_id': parent_id,
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, tb):
        pass

class TSVStream(AbstractOutputStream):
    def __init__(self, filename):
        self.filename = filename
        self.handle = None
        self.writer = None

    def __enter__(self):
        self.handle = open(self.filename, 'w', newline='')
        self.writer = csv.DictWriter(
            self.handle,
            fieldnames=[
                'comment_id',
                'permalink',
                'created_time',
                'author_username',
                'author_id',
                'comment_text',
                'comment_score',
                'comment_score_last_updated',
                'subreddit_name',
                'subreddit_id',
                'post_permalink',
                'post_title',
                'post_id',
                'post_score',
                'post_score_last_updated',
                'is_top_level',
                'parent_id',
            ],
            delimiter='\t',
            lineterminator='\n',
        )
        self.writer.writeheader()
        return self

    def __exit__(self, exc_type, exc_val, tb):
        self.handle.close()
        self.handle = None
        self.writer = None

    def write(self, data):
        self.writer.writerow(data)

class STDOutStream(AbstractOutputStream):
    def write(self, data):
        print(data['author_username'], '--', data['subreddit_name'], '@', data['created_time'], ':', data['comment_text'])

class DuplicateStream(AbstractOutputStream):
    def __init__(self, *streams):
        self.streams = streams
        self.context = None

    def __enter__(self):
        self.context = ExitStack()
        self.context.__enter__()
        for stream in self.streams:
            self.context.enter_context(stream)
        return self

    def write(self, data):
        for stream in self.streams:
            stream.write(data)

    def __exit__(self, exc_type, exc_val, tb):
        self.context.__exit__(exc_type, exc_val, tb)
        self.context = None

async def stream_comments(reddit, *subreddits):
    comments = [
        (await reddit.subreddit(sub)).stream.comments()
        for sub in subreddits
    ]

    multistream = stream.merge(*comments)
    async with multistream.stream() as source:
        async for comment in source:
            yield comment

async def main_test(*subreddits, **authorization):
    reddit = asyncpraw.Reddit(**authorization)
    try:
        print("Logged in as", await reddit.user.me())
    except:
        print("Invalid credentials")
        raise

    with DuplicateStream(STDOutStream(), TSVStream('test.tsv')) as writer:
        try:
            async for comment in stream_comments(reddit, *subreddits):
                await writer.consume(comment)
        finally:
            await reddit.close()
