# Reddit Scrapers

This directory contains code to pull live or historical
comments from reddit. It also requires an SQL database
(MySQL was used, but any database which supports SQL
  is acceptable) and Python 3.

## Data output

We highly recommend that you store comments in an SQL
database (`MYSQLStream`), although we also provide code to write data
to a TSV file (`TSVStream`) and the terminal (`STDOutStream`). You can also output to any custom
destination by creating a class which inherits from
`AbstractOutputStream` and which overrides `AbstractOutputStream.write()`.

### MySQL

The provided `MYSQLStream` class is designed to dump
comments to a MySQL database and flush every 25 comments.
To facilitate creating your own database, the expected
schema is available in **FIXME: db.sql**. This class is
built on top of [SQLAlchemy](https://www.sqlalchemy.org/)
so you could alternatively use any SQL-based database.
`MYSQLStream` expects a URL in [SQLAlchemy URL format](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls) to provide the necessary
information to connect. You may also have to install
requesite python and system packages depending on your
choice of driver. `pymysql`, the driver for MySQL, is
listed in the project requirements.

## Python Requirements

This project was tested and run on Python 3.8, but
should theoretically run on any version of Python 3 >=
3.6. The list of required packages are in **FIXME: requirements.txt**, which you can install with
`pip install -r requirements.txt`. We highly recommend
running this within a virtual environment.

## Reddit Requirements

To access the Reddit API, you must have a Reddit account,
and register a developer application on that account.
To register a developer application, follow these steps:

1. Visit https://www.reddit.com/prefs/apps
2. Click **are you a developer? create an app...**
3. Provide a name and description (these can be arbitrary)
4. Select the radio button **script** indicating that
this is not a production application
5. Provide an arbitrary redirect uri. This doesn't have
to go anywhere, but is required for the form.
6. Click **create app**
7. You should now see your application at the bottom
of the page
8. Click **edit**, if your application is not expanded
9. Make note of your **client id**, which is the bold text under the words `personal use script`, under your application name
10. Also note your **secret** which is listed only on the
expanded view, next to the word `secret`

To log into the reddit API, you will need to provide
your client id, client secret, account username,
account password, and a descriptive user agent (which can be any string). This information is used as inputs
to functions below

## Running scrapers

Our reddit scrapers and score updater are all coroutines,
built on python's asyncio library. asyncio may seem
intimidating, but it's quite simple. We will provide
examples for how to run coroutines, but if you would like
to learn more, you can read the [official documentation](https://docs.python.org/3/library/asyncio.html).

We provide two scrapers, `main_test` and `history_test`.
Both of which take a list of subreddits, and reddit api
authorization information.

### Running the live scraper

You can run the live scraper as follows:

```
run_coro(
  main_test(
    'gatech',
    'omscs',
    'otherSubreddits...',
    client_id="{your client id}",
    client_secret="{your client secret}",
    username="{your reddit username}",
    password="{your reddit password}",
    user_agent="python/ASYNCPRAW for gatech vibecheck"
  )  
)
```

This will immediately begin streaming live reddit comments from any subreddits provided in the arguments.
You can list one or more subreddits, and any strings
provided as regular positional arguments are interpreted
to be a subreddit name.

### Running the historical scraper

You can run the historical scraper as follows:

```
run_coro(
  history_test(
    "2/12/1995 - 00:00:00",
    "2/12/1996 - 01:23:34",
    'gatech',
    'omscs',
    'otherSubreddits...',
    client_id="{your client id}",
    client_secret="{your client secret}",
    username="{your reddit username}",
    password="{your reddit password}",
    user_agent="python/ASYNCPRAW for gatech vibecheck"
  )  
)
```

Most of the arguments are the same as above, with the
exception of the added date range arguments. The first
two arguments are expected to either be unix timestamps
or strings in `MM/DD/YYYY -- HH:mm:ss` format, corresponding to the desired date range in UTC.
