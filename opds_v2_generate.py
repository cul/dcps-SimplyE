# Generate OPDS v2.0 JSON from API output
import json
import os
# from pprint import pprint
import requests
from datetime import datetime
from configparser import ConfigParser

# MODE = 'EZ'
MODE = 'SAML'
MY_NAME = __file__
MY_PATH = os.path.dirname(__file__)
SCRIPT_NAME = os.path.basename(MY_NAME)
config_path = os.path.join(MY_PATH, "config.ini")
config = ConfigParser()
config.read(config_path)


API_KEY = config["API"]["springerKey"]
API_ENDPOINT = 'https://spdi.public.springernature.app/bookmeta/v1/'

ACQ_SAML_BASE_URL = 'https://fsso.springer.com/saml/login?idp=' + \
    config['IDM']['instID'] + '&targetUrl='

ACQ_EZ_BASE_URL = 'https://link-springer-com.ezproxy.cul.columbia.edu/content/pdf/10.1007%2F'

# "ePubUrl": "https://link.springer.com/download/epub/10.1007/978-1-4302-4201-7.epub"


# IMAGE_BASE_URL = 'https://media.springernature.com/w153/springer-static/cover/book/'
# IMAGE_BASE_URL = 'https://covers.springernature.com/books/jpg_width_95_pixels/'
SPRINGER_IMAGE_BASE_URL = 'https://covers.springernature.com/books/jpg_width_%s_pixels/%s.jpg'


NOW = datetime.utcnow().strftime(
    "%Y-%m-%dT%H:%M:%S.%fZ")  # Current timestamp in ISO


def main():

    # x = get_springer('978-3-319-12667-8', API_KEY)
    # print(x)

    # quit()

    # For WAYFless set
    the_books = [
        {'isbn': '978-3-319-12667-8', 'bibid': '11426193'},
        {'isbn': '978-3-0348-6082-6', 'bibid': '11969235'},
        {'isbn': '978-3-319-00639-0', 'bibid': '10808939'},
        {'isbn': '978-3-662-54961-2', 'bibid': '12858621'},
        {'isbn': '978-3-319-49688-7', 'bibid': '12821512'}
    ]

    # For EZ set
    # the_books = [
    #     {'isbn': '978-3-319-56138-7', 'bibid': '13010904'},
    #     {'isbn': '978-3-319-53139-7', 'bibid': '13414459'},
    #     {'isbn': '978-3-0348-0834-7', 'bibid': '11472568'},
    #     {'isbn': '978-3-319-10542-0', 'bibid': '11224717'},
    #     {'isbn': '978-3-319-58691-5', 'bibid': '13412684'}
    # ]

    # out_file = "springer_test_feed2.json"
    out_file = "springer_test_feed3.json"
    title = "Springer Test Feed"
    url = "https://ebooks-test.library.columbia.edu/static-feeds/springer/" + out_file
    output_dir = "output_test/springer"
    out_path = os.path.join(MY_PATH, output_dir, out_file)

    feed_dict = feed_shell(title, url)

    for b in the_books:
        x = make_springer_entry(b['isbn'], b['bibid'], mode=MODE)
        feed_dict['publications'].append(x)

    print("Saving to " + str(out_path) + "...")
    with open(out_path, "w") as f:
        json.dump(feed_dict, f)

    quit()


def make_springer_entry(_isbn, _bibid, mode='SAML'):
    clio_link = "<p><a href='https://clio.columbia.edu/catalog/" + \
        _bibid + "'>Go to catalog record in CLIO.</a></p>"
    md = get_springer(_isbn, API_KEY)
    r = md['records'][0]

    pdf_url = None
    epub_url = None
    for u in r['url']:
        if u['format'] == 'pdf':
            pdf_url = u['value']
        # if u['format'] == 'epub':
        #     epub_url = u['value']
    if 'ePubUrl' in r:
        epub_url = r['ePubUrl']

    facets = md['facets']
    subjects = []
    # print(facets)
    for f in facets:
        if f['name'] == 'subject':
            # print("YES")
            subjects += [s['value'] for s in f['values']]

    links = []
    if mode == 'SAML':
        if pdf_url:
            links.append(
                {
                    "rel": "http://opds-spec.org/acquisition",
                    "href": ACQ_SAML_BASE_URL + pdf_url,
                    "type": "application/pdf"
                }
            )
        if epub_url:
            links.append(
                {
                    "rel": "http://opds-spec.org/acquisition",
                    "href": ACQ_SAML_BASE_URL + epub_url,
                    "type": "application/epub+zip"
                }
            )
    else:
        links.append(
            {
                "rel": "http://opds-spec.org/acquisition",
                "href": ACQ_EZ_BASE_URL + _isbn + ".pdf",
                "type": "application/pdf"
            }
        )

    return {
        "metadata": {
            "@type": "http:://schema.org/EBook",
            "title": r['publicationName'],
            "author": [x['creator'] for x in r['creators']],
            # "belongsTo": {
            #     "series": "Sweetland Digital Rhetoric Collaborative"
            # },
            "description": r['abstract'] + clio_link,
            "identifier": "https://doi.org/" + r['doi'],
            "language": r['language'],
            "modified": NOW,  # should get this value from API but local for now
            "published": r['publicationDate'],
            "publisher": r['publisher'],
            "subject": subjects
        },
        "links": links,
        "images":
        [
            {
                "href": springer_img_url(648, _isbn, measure='height'),
                "type": "image/jpeg"
            },
            {
                "href": springer_img_url(125, _isbn),
                "width": 125,
                "type": "image/jpeg"
            },
            {
                "href": springer_img_url(95, _isbn),
                "width": 95,
                "type": "image/jpeg"
            }

        ]

    }


def get_springer(isbn, apikey, format='json'):
    query = format + '?q=isbn:' + isbn + '&api_key=' + \
        apikey + '/columbia-uni-api&entitlement=columbia-uni-api'
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


def springer_img_url(pixels, isbn, measure='width'):
    # pixel options: 95|125|153 (width), 648 (height)
    # Uses cover search api
    # https://covers.springernature.com/search/CoverSearch.html
    SPRINGER_IMAGE_BASE_URL = 'https://covers.springernature.com/books/jpg_%s_%d_pixels/%s.jpg'
    return SPRINGER_IMAGE_BASE_URL % (measure, pixels, str(isbn))


if __name__ == "__main__":
    main()
