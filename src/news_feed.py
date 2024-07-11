import feedparser


class Entry:
    """Represents news article"""
    def __init__(self,
                 headline: str,
                 source_link: str,
                 date_of_publication: str,
                 title: str):
        self.headline = headline
        self.source_link = source_link
        self.date_of_publication = date_of_publication
        self.title = title

        self.sentiment_score = None
        self.trend_names = None


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
                    title=entry.title
                )
                entries_list.append(entry_obj)

            return entries_list
