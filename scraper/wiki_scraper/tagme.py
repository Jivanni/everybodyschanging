import requests
import re

ENDPOINT = "https://tagme.d4science.org/tagme/tag"
LANG = "it"
# TODO: inserisci qui il tuo token
KEY = "56cd67a3-c4cc-48dd-9ecb-c20c0c31208f-843339462"

def query_tagme(text):
	payload = {"text": text, "gcube-token": KEY, "lang": LANG}
	r = requests.post(ENDPOINT, payload)
	if r.status_code != 200:
		raise Exception("Error on text: {}\n{}".format(text, r.text))
	return r.json()

def get_entities(tagme_respone, min_rho):
	ann = tagme_respone["annotations"]
	ann = [a for a in ann if a["rho"] > min_rho]
	return [a["title"] for a in ann if "title" in a]


ENDPOINT_REL = "https://tagme.d4science.org/tagme/rel"


def query_relatedness(entity1, entity2):
	tt = entity1.replace(" ", "_") + " " + entity2.replace(" ", "_")
	payload = {"tt": tt, "gcube-token": KEY, "lang": LANG}

	r = requests.post(ENDPOINT_REL, payload)
	if r.status_code != 200:
		raise Exception("Error on text: {}\n{}".format(tt, r.text))
	return r.json()
