import feedparser


class Trends:
    """Represents analytics trends"""
    def __init__(self, url):
        self.url = url

        self.keywords_list = []
        self.keywords_str = ''

    def parse(self) -> list:
        """
        Fetch current trending keywords
        :return: List with trending keywords
        """
        feed = feedparser.parse(self.url)
        keywords_list = []  # Placeholder for resulting keywords

        if feed.get('bozo', 0) == 0:  # If parsing was successful
            for entry in feed.entries:
                keywords_list.append([entry.title, entry.description.split(', ')])

        self.keywords_list = keywords_list
        return keywords_list

    def as_str(self, keywords_list=None) -> str:
        """Return keywords as string"""
        if not self.keywords_list:  # Parse RSS if it wasn't parsed before
            self.parse()

        if not keywords_list:  # Load keywords list if not given
            keywords_list = self.keywords_list

        result_str = ''
        for t in keywords_list:
            des = t[1]  # If entry has a description
            if des[0]:
                result_str += t[0] + ', ' + ', '.join(t[1]) + ', '
            else:
                result_str += t[0] + ', '

        self.keywords_str = result_str
        return result_str
