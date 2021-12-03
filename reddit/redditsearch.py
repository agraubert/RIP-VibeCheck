import aiohttp
from datetime import datetime
import asyncio

def fetch(session, **kwargs):
    #after, before, subreddit
    kwargs = {
        **{
            'metadata': 'true',
            'frequency': 'hour',
            'advanced': 'false',
            'sort': 'asc',
            'sort_type': 'created_utc',
            'size': 100
        },
        **kwargs
    }
    print("Requesting date range", kwargs['after'], '-', kwargs['before'])
    return session.get("https://api.pushshift.io/reddit/search/comment?{}".format(
        '&'.join(
            '{}={}'.format(key, val)
            for key, val in kwargs.items()
        )
    ))

class SearchRange(object):
    def __init__(self, subreddit, start, end):
        self.subreddit = subreddit
        self.start = int(start)
        self.end = int(end)

    async def query(self, reddit):
        async with aiohttp.ClientSession() as session:
            start = self.start
            print("starting query", self.subreddit)
            while True:
                # Query comments between start and end
                # We only get the first 100 results
                async with fetch(session, after=start, before=self.end, subreddit=self.subreddit) as response:
                    if not response.ok:
                        print(response.status, response.headers)
                        print(response.real_url)
                        raise ValueError("Bad request")
                    data = await response.json()
                    metadata = data['metadata']
                    print("This query:", len(data['data']), '/', metadata['total_results'])
                    for post in data['data']:
                        # Fetch comment and yield to caller
                        yield await reddit.comment(post['id'])
                        # Update search time
                        start = max(start, post['created_utc'])
                    if metadata['total_results'] < 1 or len(data['data']) >= metadata['total_results']:
                        return
                    await asyncio.sleep(2)
