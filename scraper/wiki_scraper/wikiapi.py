import wikipedia
from wikipedia import WikipediaPage
import re

WIKILANG = "it"
CONDITIONS = ["artist", "band", "gruppo", "cantautore", "cantant", "musicist", "group"]
wikipedia.set_lang(WIKILANG)


def is_singer(search_results: WikipediaPage):
    """
       This function takes a wikipedia match object
       and returns whether it belongs to a singer's wikipedia page
       ----------
       search_results : WikipediaPage
       WikipediaPage object from the wikipedia API wrapper
       Returns
       -------
       Bool
       """
    reg_exp = re.compile("|".join(CONDITIONS), flags=re.I)
    for category in search_results.categories:
        if reg_exp.search(category):
            return True
    return False


def wiki_getter(author_name: str):
    """
         This function takes the name of an artist and returns its wikipedia page as an html string
         Parameters
         ----------
         author_name: str
         String form of an author name
         Returns
         -------
         BeautifulSoup.get_html
         """
    query_matches = wikipedia.search(author_name, results=3)
    for match in query_matches:
        try:
            page = wikipedia.page(match)
            if is_singer(page):
                return wikipedia.page(page.title)
        except:
            continue
    return False


