# Generate OPDS v2.0 JSON from API output
import json
import os
from pprint import pprint
import requests
from datetime import datetime
from configparser import ConfigParser


MY_NAME = __file__
MY_PATH = os.path.dirname(__file__)
SCRIPT_NAME = os.path.basename(MY_NAME)
config_path = os.path.join(MY_PATH, "config.ini")
config = ConfigParser()
config.read(config_path)

API_KEY = config["API"]["springerKey"]
API_ENDPOINT = 'http://api.springernature.com/bookmeta/v1/'

ACQ_BASE_URL = 'https://fsso.springer.com/saml/login?idp=' + \
    config['IDM']['instID'] + '&targetUrl='

IMAGE_BASE_URL = 'https://media.springernature.com/w153/springer-static/cover/book/'
NOW = datetime.utcnow().strftime(
    "%Y-%m-%dT%H:%M:%S.%fZ")  # Current timestamp in ISO


def main():

    the_isbns = [
        '978-3-319-12667-8',
        '978-3-0348-6082-6',
        '978-3-319-00639-0',
        '978-3-662-54961-2',
        '978-3-319-49688-7'
    ]

    out_file = "springer_test_feed.json"
    title = "Springer Test Feed"
    url = "https://ebooks-test.library.columbia.edu/static-feeds/springer/"
    + out_file
    output_dir = "output_test/springer"
    out_path = os.path.join(MY_PATH, output_dir, out_file)

    feed_dict = feed_shell(title, url)

    for i in the_isbns:
        x = make_springer_entry(i)
        feed_dict['publications'].append(x)

    print("Saving to " + str(out_path) + "...")
    with open(out_path, "w") as f:
        json.dump(feed_dict, f)

    quit()


def make_springer_entry(_isbn):
    md = get_springer(_isbn, API_KEY)
    r = md['records'][0]

    pdf_url = None
    epub_url = None
    for u in r['url']:
        if u['format'] == 'pdf':
            pdf_url = u['value']
        if u['format'] == 'epub':
            epub_url = u['value']

    facets = md['facets']
    subjects = []
    # print(facets)
    for f in facets:
        if f['name'] == 'subject':
            # print("YES")
            subjects += [s['value'] for s in f['values']]

    links = []
    if pdf_url:
        links.append(
            {
                "rel": "http://opds-spec.org/acquisition",
                "href": ACQ_BASE_URL + pdf_url,
                "type": "application/pdf"
            }
        )
    if epub_url:
        links.append(
            {
                "rel": "http://opds-spec.org/acquisition",
                "href": ACQ_BASE_URL + epub_url,
                "type": "application/epub+zip"
            }
        )

    record = {
        "metadata": {
            "@type": "http:://schema.org/EBook",
            "title": r['publicationName'],
            "author": [x['creator'] for x in r['creators']],
            # "belongsTo": {
            #     "series": "Sweetland Digital Rhetoric Collaborative"
            # },
            "description": r['abstract'],
            "identifier": r['identifier'],
            "language": "eng",  # static for now
            "modified": NOW,  # should get this value from API but local for now
            "published": r['publicationDate'],
            "publisher": r['publisher'],
            "subject": subjects
        },
        "links": links,
        "images":
        [
            {
                "href": IMAGE_BASE_URL + r['isbn'] + ".jpg",
                "width": 200,
                "type": "image/jpeg"
            }
        ]

    }
    return record


def get_springer(isbn, apikey, format='json'):
    query = format + '?q=isbn:' + isbn + '&api_key=' + apikey
    try:
        response = requests.get(API_ENDPOINT + query)
        response.raise_for_status()
    except Exception as err:
        print('*** get_springer request error: ' + str(err))
    else:
        # If the response was successful, no exception will be raised
        x = json.loads(response.content)
        if x['result'][0]['total'] == '1':
            return x
        print("Number of responses != 1: skipping!")  # debug


def feed_shell(_title, _url):
    return {
        "metadata": {
            "title": _title
        },
        "links": [
            {
                "rel": "self",
                "href": _url,
                "type": "application/opds+json"
            }
        ],
        "publications": []
    }


if __name__ == "__main__":
    main()
