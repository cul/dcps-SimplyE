# Generate OPDS v2.0 JSON from API output
import json
import os
import re
import requests
import sys
from datetime import datetime
from configparser import ConfigParser
from dcps.pickle_utils import unpickle_it

MY_NAME = __file__
MY_PATH = os.path.dirname(__file__)
SCRIPT_NAME = os.path.basename(MY_NAME)
config_path = os.path.join(MY_PATH, "config.ini")
config = ConfigParser()
config.read(config_path)


API_ENDPOINT = 'https://api.springernature.com/bookmeta/v1/'
API_KEY = config["SPRINGER"]["apiKey"]
ENTITLEMENT_ID = config["API"]["entitlementID"]
PER_PAGE = 100


ACQ_SAML_BASE_URL = 'https://fsso.springer.com/saml/login?idp=' + \
    config['IDM']['instID'] + '&targetUrl='

ACQ_EZ_BASE_URL = 'https://link-springer-com.ezproxy.cul.columbia.edu/content/pdf/10.1007%2F'

SPRINGER_IMAGE_BASE_URL = 'https://covers.springernature.com/books/jpg_width_%s_pixels/%s.jpg'


NOW = datetime.utcnow().strftime(
    "%Y-%m-%dT%H:%M:%S.%fZ")  # Current timestamp in ISO


def main():
    isbn = sys.argv[1]
    unpunctuated = re.compile('^\d{13}$', re.IGNORECASE)
    if unpunctuated.match(isbn):
        # 9783030561680 -> 978-3-030-56168-0
        segments = [isbn[0:3], isbn[3], isbn[4:7], isbn[7:12], isbn[12]]
        isbn = '-'.join(segments)
    feed_stem = "springer_test_isbn_feed"
    collection_title = "springer"
    out_file = feed_stem + ".json"
    title = "Springer Test Feed"
    url = "https://ebooks-test.library.columbia.edu/static-feeds/springer/" + \
        out_file
    output_dir = "output_test/springer"
    os.makedirs(output_dir, exist_ok=True)
    subject_path = os.path.join(
        MY_PATH, 'output_test/springer/springer_subjects.pickle')

    datastore_path = springer_build_datastore(feed_stem, collection_title, subject_path,
                             output_dir,
                             [isbn])

    springer_build_opds(datastore_path,
                        'Springer Test Feed', url, 'output_test/springer/springer_test_feed_isbn_OPDS.json')

def springer_build_opds(data_store_path, feed_title, url, output_path):
    """Given stored JSON API data, compose and save OPDS v2 feed.

    Args:
        data_store_path (uri): Local path to JSON data store (as retrieved from API)
        feed_title (str): short title of feed
        url (url): The URL that will appear as the self object of the feed
        output_path (uri): Local path to output file
    """
    if os.access(data_store_path, os.F_OK):
        with open(data_store_path, "rb") as f:
            json_data = json.load(f)
    else:
        json_data = {}

    feed_dict = feed_shell(feed_title, url)

    for i in json_data:
        isbn = i['isbn']
        identifier = i['identifier']
        print(isbn)
        print(identifier)
        entry = make_springer_entry(i)
        feed_dict['publications'].append(entry)

    print("Saving to " + str(output_path) + "...")
    with open(output_path, "w") as f:
        json.dump(feed_dict, f, indent=2)

def springer_build_datastore(feed_stem, collection_title,
                             subject_path,
                             output_dir,
                             isbns):
    """Capture and store API data, merging with CUL-specific metadata.

    Args:
        feed_stem (str): short string used in file naming (no spaces)
        collection_title (str): Display title of the feed
        subject_path (str): Path to local subject lookup table
        output_dir (str): Path to local ouput directory
        query (str, optional): Boundary parameters for API request. Defaults to 'onlinedatefrom:2001-01-01%20onlinedateto:2021-07-31'.

    Returns:
        None: Saves to file; does not return data
    """
    out_file = feed_stem + ".json"
    url = "https://ebooks-test.library.columbia.edu/static-feeds/springer/" + \
        out_file

    data_store = os.path.join(output_dir, feed_stem + '_datastore.json')

    subject_data = unpickle_it(subject_path)

    x =  [get_springer_by_isbn(isbn) for isbn in isbns]

    with open(os.path.join(output_dir, feed_stem + '_cache.json'), "w") as f:
        json.dump(x, f, indent=2)


    print("Retrieved " + str(len(x)) + " books.")
    for r in x:
        # TODO: look up bibids
        r['cul_metadata'] = {'bibid': 'XXXXXX',
                             'feed_id': feed_stem,
                             'collection_name':
                             collection_title,
                             'retrieved': NOW}

        try:
            r['subjects'] = subject_data[r['doi']]
        except KeyError:
            r['subjects'] = []
            print("Warning: no subjects found for " + str(r['identifier']))
    if os.path.exists(data_store):
        # m = springer_merge_records(x, data_store)
        print("Saving " + str(len(x)) + " records to " + str(data_store) + "...")
        with open(data_store, "w") as f:
            json.dump(x, f)
        print("Update of " + str(data_store) + " complete.")
    else:
        print("Saving to " + str(data_store) + "...")
        with open(data_store, "w") as f:
            json.dump(x, f)
    return data_store

def springer_merge_records(data, filepath):
    """insert new records, and replace duplicate ones with new ones. Treats any duplicate record in <data> as newer (does not compare dates)

    Args:
        data (dict): New records to include
        filepath (str): Path to existing file to merge into

    Returns:
        dict: dict representation of merged data
    """
    with open(filepath, "rb") as f:
        saved_data = json.load(f)
    # saved_data_ids = [r['identifier'] for r in saved_data]
    data_ids = [r['identifier'] for r in data]
    print(data_ids)
    new_data = []
    for sdr in saved_data:
        if sdr['identifier'] in data_ids:
            # find the replacement record and insert instead.
            for dr in data:
                if dr['identifier'] == sdr['identifier']:
                    print("Updating record " + str(dr['identifier']))
                    new_data.append(dr)
        else:
            new_data.append(sdr)
    return new_data


def feed_shell(_title, _url):
    """Generate a dict representing the JSON feed shell without publication data (to be added)

    Args:
        _title (str): Title used in metadata/title element
        _url (str): URL used in links/href element

    Returns:
        [type]: [description]
    """
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


def get_springer_batch(q=None, per_page=PER_PAGE, _format='json'):
    """Retrieve a batch of Springer records from API

    Args:
        q (str, optional): An API query string. Defaults to None.
        per_page (int, optional): Number of records per page. Defaults to PER_PAGE.
        _format (str, optional): Format parameter. Defaults to 'json'.

    Returns:
        [type]: [description]
    """
    q_string = 'q=' + q + '&' if q else ''
    params = '?' + q_string + 's={}' + '&p=' + \
        str(per_page) + '&api_key=' + API_KEY
    entitlement = '/' + ENTITLEMENT_ID + '&entitlement=' + ENTITLEMENT_ID
    # print(params % (1))
    url_str = API_ENDPOINT + _format + \
        params + entitlement

    total = springer_get_count(url_str.format(str(1)))

    c = 1
    the_data = []
    while c < total:
        the_data += get_springer_records(url_str.format(str(c)))
        c += per_page
    return (the_data)


def get_springer_records(url):
    """Retrieve Springer records from API

    Args:
        url (str): URL to request

    Returns:
        dict: dict representation of records in JSON response
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as err:
        print('*** get_springer_records request error: ' + str(err))
    else:
        # If the response was successful, no exception will be raised
        x = json.loads(response.content)
        # print(x)
        return x['records']


def springer_get_count(url):
    """Find out how many total records the API will return. Only requests page 1.

    Args:
        url (str): URL to request

    Returns:
        int: Count of records as reported in page 1 of API response.
    """
    try:
        initial_page = requests.get(url)
        initial_page.raise_for_status()
    except Exception as err:
        print('*** get_springer_count request error: ' + str(err))
    else:
        # If the response was successful, no exception will be raised
        x = json.loads(initial_page.content)
        # print(x)
        return int(x['result'][0]['total'])


def make_springer_entry(record, mode='SAML'):
    """Create an OPDS record entry

    Args:
        record (dict): Dict representation of API record
        mode (str, optional): Type of acquistion links to use (SAML|EZPROXY). Defaults to 'SAML'.

    Returns:
        dict: Dict representation fo an OPDS record entry
    """
    bibid = record['cul_metadata']['bibid']
    clio_link = "<p><a href='https://clio.columbia.edu/catalog/{}'>Go to catalog record in CLIO.</a></p>".format(
        str(bibid))
    isbn = record['isbn']
    pdf_url = None
    epub_url = None
    for u in record['url']:
        if u['format'] == 'pdf':
            pdf_url = u['value']
    if 'ePubUrl' in record:
        epub_url = record['ePubUrl']

    subjects = record['subjects']

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
                "href": ACQ_EZ_BASE_URL + isbn + ".pdf",
                "type": "application/pdf"
            }
        )

    return {
        "metadata": {
            "@type": "http:://schema.org/EBook",
            "title": record['publicationName'],
            # TODO: non-author contributors (bookEditors)
            "author": [{'name': x['creator']} for x in record['creators']],
            "editor": [{'name': x['bookEditor']} for x in record['bookEditors']],
            "description": record['abstract'] + clio_link,
            "identifier": "https://doi.org/" + record['doi'],
            "language": record['language'],
            "modified": NOW,  # should get this value from API but local for now
            "published": record['publicationDate'],
            "publisher": record['publisher'],
            "subject": subjects
        },
        "links": links,
        "images":
        [
            {
                "href": springer_img_url(648, isbn, measure='height'),
                "type": "image/jpeg"
            },
            {
                "href": springer_img_url(125, isbn),
                "width": 125,
                "type": "image/jpeg"
            },
            {
                "href": springer_img_url(95, isbn),
                "width": 95,
                "type": "image/jpeg"
            }

        ]

    }


def get_springer_by_isbn(isbn, apikey=API_KEY, format='json'):
    """Retrieve single OPDS record from API by ISBN

    Args:
        isbn (str): ISBN
        apikey (str, optional): Defaults to API_KEY.
        format (str, optional): API response format. Defaults to 'json'.

    Returns:
        dict: Representation of API record
    """
    query = format + '?q=isbn:' + isbn + '&api_key=' + apikey
    try:
        print(API_ENDPOINT + query)
        response = requests.get(API_ENDPOINT + query)
        response.raise_for_status()
    except Exception as err:
        print('*** get_springer request error: ' + str(err))
    else:
        # If the response was successful, no exception will be raised
        x = json.loads(response.content)
        if x['result'][0]['total'] == '1':
            isbn_result = x['records'][0]
            isbn_result['subjects'] = []
            if 'facets' in x:
                for facet in x['facets']:
                    if facet['name'] == 'subject':
                        isbn_result['subjects'] = [value['value'] for value in facet['values']]
            return isbn_result
        print("Number of responses != 1: skipping!")  # debug


def springer_img_url(pixels, isbn, measure='width'):
    """Compose a cover image URL. Uses cover search api https://covers.springernature.com/search/CoverSearch.html

    Args:
        pixels (int): pixel options 95|125|153 (width), 648 (height)
        isbn (str): ISBN
        measure (str, optional): Either width or height. Defaults to 'width'.

    Returns:
        str: URL
    """
    SPRINGER_IMAGE_BASE_URL = 'https://covers.springernature.com/books/jpg_%s_%d_pixels/%s.jpg'
    return SPRINGER_IMAGE_BASE_URL % (measure, pixels, str(isbn))


if __name__ == "__main__":
    main()
