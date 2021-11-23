import asyncio
import asyncpraw
from aiostream import stream
from datetime import datetime
from abc import ABC, abstractmethod
import csv
from contextlib import ExitStack
from .db import Database
from pymysql import IntegrityError
import os
from .redditsearch import SearchRange

TIMESTAMP_FORMAT = "%m/%d/%Y - %H:%M:%S"

def safe_getattr(obj, attr):
    if obj is not None and hasattr(obj, attr):
        return getattr(obj, attr)

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
        if author is not None:
            await author.load()
        sub = comment.subreddit
        if sub is not None:
            await sub.load()
        post = comment.submission
        if post is not None:
            await post.load()
        parent_id = comment.parent_id
        is_top_level = parent_id.startswith('t3_')
        now = datetime.now().strftime(TIMESTAMP_FORMAT)
        return {
            'comment_id': safe_getattr(comment, 'id'),
            'permalink': safe_getattr(comment, 'permalink'),
            'created_time': datetime.fromtimestamp(comment.created).strftime(TIMESTAMP_FORMAT),
            'author_username': safe_getattr(author, 'name'),
            'author_id': safe_getattr(author, 'id'),
            'comment_text': safe_getattr(comment, 'body'),
            'comment_score': safe_getattr(comment, 'score'),
            'comment_score_last_updated': now,
            'subreddit_name': safe_getattr(sub, 'display_name'),
            'subreddit_id': safe_getattr(sub, 'id'),
            'post_permalink': safe_getattr(post, 'permalink'),
            'post_title': safe_getattr(post, 'title'),
            'post_id': safe_getattr(post, 'id'),
            'post_score': safe_getattr(post, 'score'),
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

class MYSQLStream(AbstractOutputStream):
    def __init__(self, url, **kwargs):
        self.db = Database(url, **kwargs)
        self.inserts = 0

    def __enter__(self):
        self.db.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, tb):
        self.db.__exit__(exc_type, exc_val, tb)

    def write(self, data):
        if isinstance(data['created_time'], str):
            data['created_time'] = datetime.strptime(data['created_time'], TIMESTAMP_FORMAT)
        if isinstance(data['comment_score_last_updated'], str):
            data['comment_score_last_updated'] = datetime.strptime(data['comment_score_last_updated'], TIMESTAMP_FORMAT)
        if isinstance(data['post_score_last_updated'], str):
            data['post_score_last_updated'] = datetime.strptime(data['post_score_last_updated'], TIMESTAMP_FORMAT)
        if not len(self.db.query(self.db['comments'].select.where(self.db['comments'].c.comment_id == data['comment_id']))):
            self.db.insert('comments', **data)
        self.inserts += 1
        if self.inserts % 25 == 0:
            self.db.commit()

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

async def stream_historical_comments(reddit, start, stop, *subreddits):
    ranges = [
        SearchRange(sub, start, stop).query(reddit) for sub in subreddits
    ]
    print("there are", len(ranges), "query ranges")
    multistream = stream.merge(*ranges)
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

    with DuplicateStream(STDOutStream(), MYSQLStream(os.environ['VIBE_DB'], tables=['comments'])) as writer:
        try:
            async for comment in stream_comments(reddit, *subreddits):
                await writer.consume(comment)
        finally:
            await reddit.close()

async def history_test( start, stop, *subreddits, **authorization):
    if isinstance(start, str):
        start = datetime.strptime(start, TIMESTAMP_FORMAT).timestamp()
    if isinstance(stop, str):
        stop = datetime.strptime(stop, TIMESTAMP_FORMAT).timestamp()
    reddit = asyncpraw.Reddit(**authorization)
    try:
        print("Logged in as", await reddit.user.me())
    except:
        print("Invalid credentials")
        raise


    try:
        with DuplicateStream(STDOutStream(), MYSQLStream(os.environ['VIBE_DB'], tables=['comments'])) as writer:
            async for comment in stream_historical_comments(reddit, start, stop, *subreddits):
                await writer.consume(comment)
    finally:
        await reddit.close()

def run_coro(coroutine):
    asyncio.run(coroutine)
