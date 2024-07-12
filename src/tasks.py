from src.celery_config import celery_app

import os
import logging
from dotenv import load_dotenv

from src.models import EntryModel
from src.news_feed import Feed, filter_news
from src.trends_analytics import Trends
from src.database import DB
from src.openai_client import OpenAIClient

load_dotenv()

FEED_RSS_URL = 'https://tsn.ua/rss/full.rss'
TRENDS_ANALYTICS_RSS_URL = 'https://trends.google.com/trends/trendingsearches/daily/rss?geo=UA'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEVELOPER_MODE = os.getenv("DEVELOPER_MODE")  # Limits amount of articles given to LLM; for developing purposes
if DEVELOPER_MODE == 'false':
    DEVELOPER_MODE = False
else:
    DEVELOPER_MODE = True


def fetch_and_refresh():
    """Fetches news data and refreshes database."""

    def get_sentiment_score(entries_list, developer_mode=DEVELOPER_MODE):
        """Make OpenAI call to get sentiment score"""
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            openai_client = OpenAIClient(api_key=openai_api_key)
        else:
            raise SystemError('Set OpenAI API key to continue')

        logger.info('Calling API to get sentiment score of article titles...')
        entries_titles = [entry.title for entry in entries_list]
        sentiment_score_list = openai_client.get_sentiment_score(entries_titles, developer_mode=developer_mode)

        # Append them to objects
        sentiment_score_list_len = len(sentiment_score_list)
        for i, entry in enumerate(entries_list):
            if i < sentiment_score_list_len:
                entry.sentiment_score = sentiment_score_list[i]
            else:
                continue

        return entries_list

    # Fetch news data and filter it with trends
    feed = Feed(FEED_RSS_URL)
    articles = feed.parse()
    logger.info('News articles fetched')

    trends = Trends(TRENDS_ANALYTICS_RSS_URL)
    keys_list = trends.parse()
    keys_str = trends.as_str(keys_list)
    logger.info('Trends keywords fetched')

    trending_news = filter_news(articles, keys_str)
    logger.info('News articles filtered')

    # Init database and load previous dataset
    database = DB()
    entries = database.get_all_entries()

    if entries:

        print(f'Fetched {len(entries)} existing entries from database')

        old_entries_titles = [e.title for e in entries]

        resulting_entries = []  # Placeholder for resulting entries
        new_entries = []  # Placeholder for new entries from trending news, that weren't in old dataset

        for e in trending_news:
            if e.title in old_entries_titles:
                sentiment_score = [old_entry.sentiment_score for old_entry in entries if old_entry.title == e.title]
                if sentiment_score[0]:
                    e.sentiment_score = sentiment_score[0]
                else:  # If fetched entry doesn't have sentiment score. This can happen, if list of articles didn't fit LLM context window, so not all articles were processed
                    new_entries.append(e)
                    continue

                resulting_entries.append(e)
            else:  # If it's new entry that didn't exist in old dataset, we need to calculate sentiment score.
                new_entries.append(e)

        if new_entries:
            new_entries = get_sentiment_score(new_entries)
            resulting_entries += new_entries
            logger.info('New articles sentiment score fetched, refreshing database...')

        database.delete_all_entries()
        for entry in resulting_entries:
            entry_model = EntryModel(
                headline=entry.headline,
                source_link=entry.source_link,
                date_of_publication=entry.date_of_publication,
                title=entry.title,
                fulltext=entry.fulltext,
                sentiment_score=entry.sentiment_score,
                trend_names=entry.trend_names
            )
            database.add_entry(entry_model)
        logger.info('Data refreshed')

        database.close_db()

    else:  # If it's first launch of the system
        trending_news = get_sentiment_score(trending_news)
        logger.info(f'Articles sentiment score fetched, writing it to database...')

        for entry in trending_news:
            entry_model = EntryModel(
                headline=entry.headline,
                source_link=entry.source_link,
                date_of_publication=entry.date_of_publication,
                title=entry.title,
                fulltext=entry.fulltext,
                sentiment_score=entry.sentiment_score,
                trend_names=entry.trend_names
            )
            database.add_entry(entry_model)
        logger.info('Data added')

    database.close_db()


@celery_app.task
def refresh_function():
    fetch_and_refresh()
