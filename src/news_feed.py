import feedparser
from bs4 import BeautifulSoup


class Entry:
    """Represents news article"""
    def __init__(self,
                 headline: str,
                 source_link: str,
                 date_of_publication: str,
                 title: str,
                 fulltext: str):
        self.headline = headline
        self.source_link = source_link
        self.date_of_publication = date_of_publication
        self.title = title
        self.fulltext = fulltext

        self.sentiment_score = None
        self.trend_names = ''  # Placeholder for matched keywords


class Feed:
    """Represents RSS feed"""
    def __init__(self, url: str) -> None:
        """
        :param url: URL to RSS source
        """
        self.url = url

    def parse(self) -> list[Entry]:
        """
        Fetch articles from RSS source and represent them as objects.
        :return: List of articles as Entry objects.
        """
        feed = feedparser.parse(self.url)
        entries_list = []  # Placeholder for resulting entries

        if feed.get('bozo', 0) == 0:  # If parsing was successful
            for entry in feed.entries:
                entry_obj = Entry(
                    headline=entry.description,
                    source_link=entry.link,
                    date_of_publication=entry.published,
                    title=entry.title,
                    fulltext=BeautifulSoup(entry.fulltext, features="html.parser").get_text()  # Convert HTML to pure text
                )
                entries_list.append(entry_obj)

            return entries_list


def filter_news(entries: list[Entry], keywords: str) -> list[Entry]:
    """Filter given entries by presence of keywords in article text"""
    keywords_list = keywords.split(' ')

    # Process each word so there will be only alphabetical characters and it will be lowercase
    keywords_list_filtered = []
    for word in keywords_list:
        word = ''.join([char for char in word if char.isalpha()])
        if len(word) > 3:  # Filter out words that don't have semantic meaning (and, or, etc.) - usually it's words with less than 3 characters
            keywords_list_filtered.append(word.lower())

    # Process every word in article text, and if there will be any match with at least one word in trends -
    # save this article
    filtered_articles = []

    for entry in entries:
        # Convert article text to lowercase with only alphabetic characters and whitespaces present.
        article_text_filtered = ''.join([char for char in entry.fulltext if char.isalpha() or char.isspace()]).lower()

        for word in article_text_filtered.split(' '):
            if word in keywords_list_filtered:
                if word not in entry.trend_names.split(', '):
                    if entry.trend_names:
                        entry.trend_names += ', ' + word
                    else:
                        entry.trend_names += word
                if entry not in filtered_articles:
                    filtered_articles.append(entry)

    return filtered_articles
