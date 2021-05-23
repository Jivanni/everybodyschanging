import requests
import re

WIKILANG = "it"
CONDITIONS = ["artist", "band", "gruppo", "cant", "musicist", "group", "rap", "singer", "compo"]
ENDPOINT = f"https://{WIKILANG}.wikipedia.org/w/api.php"

REG_EXP = re.compile("|".join(CONDITIONS), flags=re.I)

PARAMS = {
    "action": "opensearch",
    "namespace": "0",
    "search": "",
    "limit": "5",
    "format": "json"
}

def wiki_getter(session_object, author_name):
    PARAMS["search"] = author_name
    query = session_object.get(url=ENDPOINT, params=PARAMS)
    query.raise_for_status()
    query_text, matches, descriptions, links = query.json()

    if len(matches) == 0:
        return (None, None)
    for i in range(len(matches)-1):
        if re.search(r"(disco|video|filmo)gra",matches[i], flags= re.I):
            continue
        if REG_EXP.search(matches[i]):
            return (matches[i],links[i]) #, matches)
    return (matches[0], links[0]) #, matches)
