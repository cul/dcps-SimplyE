# Generate OPDS v2.0 JSON from API output
import json
import os
from pickle import APPEND
from pprint import pprint
import requests
from datetime import datetime
from configparser import ConfigParser
import dcps_utils as util


MY_NAME = __file__
MY_PATH = os.path.dirname(__file__)
SCRIPT_NAME = os.path.basename(MY_NAME)
config_path = os.path.join(MY_PATH, "config.ini")
config = ConfigParser()
config.read(config_path)


API_ENDPOINT = 'https://spdi.public.springernature.app/bookmeta/v1/'
API_KEY = config["API"]["springerKey"]
ENTITLEMENT_ID = config["API"]["entitlementID"]
PER_PAGE = 100


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

    feed_stem = "springer_test_feed5"
    collection_title = "springer"
    out_file = feed_stem + ".json"
    title = "Springer Test Feed"
    url = "https://ebooks-test.library.columbia.edu/static-feeds/springer/" + \
        out_file
    output_dir = "output_test/springer"
    pickle_path = os.path.join(output_dir, feed_stem + '.pickle')

    data_store = os.path.join(output_dir, feed_stem + '_datastore.json')

    out_path = os.path.join(MY_PATH, output_dir, out_file)

    output = []

    subject_path = os.path.join(
        MY_PATH, 'output_test/springer/springer_subjects.pickle')

    subject_data = util.unpickle_it(subject_path)

    x = get_springer_batch(
        q='onlinedatefrom:2001-01-01%20onlinedateto:2021-07-31')

    print("Retrieved " + str(len(x)) + " books.")
    for r in x:
        r['cul_metadata'] = {'bibid': 'XXXXXX',
                             'feed_id': feed_stem,
                             'collection_name':
                             collection_title,
                             'retrieved': NOW}
        doi = r['doi']
        try:
            r['subjects'] = subject_data[doi]
        except KeyError:
            print("Warning: no subjects found for " + str(r['identifier']))

    if os.path.exists(data_store):
        x = springer_merge_records(x, data_store)
        print("Saving " + str(len(x)) + " records to " + str(data_store) + "...")
        with open(data_store, "w") as f:
            json.dump(x, f)
        return "Update of " + str(data_store) + " complete."
    else:
        print("Saving to " + str(data_store) + "...")
        with open(data_store, "w") as f:
            json.dump(x, f)

    # pprint(x)
    quit()
    for i in x:
        isbn = i['isbn']
        identifier = i['identifier']
        print(isbn)
        print(identifier)
        bibid = '9999999'  # TODO: replace with lookup
        book_data = get_springer_by_isbn(isbn)
        output.append(book_data)
        # pprint(book_data)
        # entry = make_springer_entry(book_data, bibid)
        # feed_dict['publications'].append(entry)

    print("Saving to " + str(pickle_path) + "...")

    util.pickle_it(output, pickle_path)

    x = util.unpickle_it(pickle_path)

    feed_dict = feed_shell(title, url)

    for i in x:
        # isbn = i['isbn']
        # print(isbn)
        bibid = '9999999'  # TODO: replace with lookup
        # book_data = get_springer_by_isbn(isbn)
        # output.append(book_data)
        # pprint(book_data)
        entry = make_springer_entry(i, bibid)
        feed_dict['publications'].append(entry)

    print("Saving to " + str(out_path) + "...")
    with open(out_path, "w") as f:
        json.dump(feed_dict, f)

    # pprint(x[0])
    print(len(x))

    quit()


def springer_merge_records(data, filepath):
    # insert new records, and replace duplicate ones with new ones
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


def get_springer_batch(q=None, per_page=PER_PAGE, format='json'):
    q_string = 'q=' + q + '&' if q else ''
    params = '?' + q_string + 's={}' + '&p=' + \
        str(per_page) + '&api_key=' + API_KEY
    entitlement = '/' + ENTITLEMENT_ID + '&entitlement=' + ENTITLEMENT_ID
    # print(params % (1))
    url_str = API_ENDPOINT + format + \
        params + entitlement

    total = springer_get_count(url_str.format(str(1)))

    c = 1
    the_data = []
    while c < total:
        the_data += get_springer_records(url_str.format(str(c)))
        c += per_page
    return (the_data)


def get_springer_records(url):
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


def make_springer_entry(data, bibid, mode='SAML'):
    clio_link = "<p><a href='https://clio.columbia.edu/catalog/{}'>Go to catalog record in CLIO.</a></p>".format(
        str(bibid))
    record = data['records'][0]
    facets = data['facets']
    isbn = record['isbn']
    pdf_url = None
    epub_url = None
    for u in record['url']:
        if u['format'] == 'pdf':
            pdf_url = u['value']
        # if u['format'] == 'epub':
        #     epub_url = u['value']
    if 'ePubUrl' in record:
        epub_url = record['ePubUrl']

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
                "href": ACQ_EZ_BASE_URL + isbn + ".pdf",
                "type": "application/pdf"
            }
        )

    return {
        "metadata": {
            "@type": "http:://schema.org/EBook",
            "title": record['publicationName'],
            # TODO: non-author contributors (editors)
            "author": [x['creator'] for x in record['creators']],
            # "belongsTo": {
            #     "series": "Sweetland Digital Rhetoric Collaborative"
            # },
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


def springer_img_url(pixels, isbn, measure='width'):
    # pixel options: 95|125|153 (width), 648 (height)
    # Uses cover search api
    # https://covers.springernature.com/search/CoverSearch.html
    SPRINGER_IMAGE_BASE_URL = 'https://covers.springernature.com/books/jpg_%s_%d_pixels/%s.jpg'
    return SPRINGER_IMAGE_BASE_URL % (measure, pixels, str(isbn))


if __name__ == "__main__":
    main()
