import json
import os
from pprint import pprint
import dcps_utils as util
from configparser import ConfigParser
import requests

MY_PATH = os.path.dirname(__file__)
config_path = os.path.join(MY_PATH, "config.ini")
config = ConfigParser()
config.read(config_path)

PQ_FEED_URL = config["FEED"]["proquestFeedURL"]
PER_PAGE = 2000


# Get proxy url if there is one.
if "httpsProxy" in config["PROXIES"]:
    HTTPS_PROXY = config["PROXIES"]["httpsProxy"]
else:
    HTTPS_PROXY = None

BIBID_LOOKUP_PATH = os.path.join(
    MY_PATH, "proquest_lookup.json")

# FEED_PATH = os.path.join(
#     MY_PATH, "output_test/proquest/ProQuest_BooksCatalog.json")

EPUB_OUT_PATH = os.path.join(
    MY_PATH, "output_test/proquest/proquest_books_catalog_epub.json")

PDF_OUT_PATH = os.path.join(
    MY_PATH, "output_test/proquest/proquest_books_catalog_pdf.json")


def main():

    input_feed_url = PQ_FEED_URL + "?page=1&hitsPerPage=" + str(PER_PAGE)

    print("Retrieving data from " + input_feed_url)

    feed_data = get_proquest_feed(input_feed_url)

    print("")
    print("Assembling EPUB feed ...")

    epub_opds = build_proquest_opds(feed_data, feed_type="epub")

    api_response = api_wrap(epub_opds)

    print("Saving " + str(len(epub_opds['publications'])) +
          " records to " + str(EPUB_OUT_PATH) + "...")
    with open(EPUB_OUT_PATH, "w") as f:
        json.dump(api_response, f)

    print("")
    print("Assembling PDF feed ...")

    pdf_opds = build_proquest_opds(feed_data, feed_type="pdf")

    api_response = api_wrap(pdf_opds)

    print("Saving " + str(len(pdf_opds['publications'])) +
          " records to " + str(PDF_OUT_PATH) + "...")
    with open(PDF_OUT_PATH, "w") as f:
        json.dump(api_response, f)

    quit()


def get_proquest_feed(url):
    """Retrieve data from ProQuest API using given URL. Note that only whitelisted IP are allowed.

    Args:
        url (str): ProQuest feed URL

    Returns:
        dict: dict representation of JSON feed
    """
    print(url)
    print(HTTPS_PROXY)
    try:
        if HTTPS_PROXY:
            response = requests.get(
                url, proxies={"https": HTTPS_PROXY}
            )
        else:
            response = requests.get(url)
        response.raise_for_status()
    except Exception as err:
        raise Exception('*** get_proquest_feed request error: ' + str(err))
    else:
        # If the response was successful, no exception will be raised
        try:
            res = json.loads(response.text)
            a_book = json.loads(response.text)[
                'opdsFeed']['groups'][0]['publications'][0]
        except json.decoder.JSONDecodeError:
            raise Exception("*** ERROR: Could not parse JSON data at " + url)
        except TypeError:
            raise Exception("*** Expected Data not found at " + url)

        return res


def api_wrap(opds_feed):
    """Take the OPDS data and wrap in the custom ProQuest API response.

    Args:
        opds_feed (dict): dict representation of OPDS feed JSON

    Returns:
        dict: dict representation of API JSON response.
    """
    return {
        "status": "Success",
        "statusCode": 200,
        "statusMsg": "OK",
        "opdsFeed": opds_feed
    }


def build_proquest_opds(feed_data, feed_type="all"):
    """Compose a filtered OPDS2 feed, merging CLIO data with records

    Args:
        feed_data (dict): dict representation of JSON data from PQ feed.
        feed_type (str, optional): Select "epub" or "pdf" to filter. Defaults to "all".

    Returns:
        dict: dict representation of OPDS feed.
    """

    the_books = feed_data['opdsFeed']['groups'][0]['publications']

    opds_feed = {
        "metadata": {
            "title": "Books Catalog Opds Feed",
            "itemsPerPage": 1500,
            "numberOfItems": 0
        },
        "links": [{
            "href": "https://drafts.opds.io/schema/feed.schema.json",
            "type": "application/opds+json",
            "rel": "self",
            "alternate": [],
            "children": []
        }],
        "publications": []
    }
    pubs = []
    for b in the_books:
        docid = b['metadata']['identifier'].split('/')[-1]
        bibid = get_bibid(docid)
        if not bibid:
            # There is no catalog record; skip this one
            continue
        link_info = get_type(b['links'])
        # TODO: Refactor this switch section
        if feed_type == "epub":
            # Feed with only epubs
            if link_info['has_epub']:
                if 'description' not in b['metadata']:
                    b['metadata']['description'] = ''
                b['metadata']['description'] = add_bibid(
                    b['metadata']['description'], bibid)
                pubs.append(b)
        elif feed_type == "pdf":
            # Feed with only pdfs
            if link_info['has_pdf'] and not link_info['has_epub']:
                if 'description' not in b['metadata']:
                    b['metadata']['description'] = ''
                b['metadata']['description'] = add_bibid(
                    b['metadata']['description'], bibid)
                pubs.append(b)
        else:
            # Feed with both epubs and pdfs
            if 'description' not in b['metadata']:
                b['metadata']['description'] = ''
            b['metadata']['description'] = add_bibid(
                b['metadata']['description'], bibid)
            pubs.append(b)
    opds_feed['metadata']['numberOfItems'] = len(pubs)
    opds_feed['publications'] = pubs
    return opds_feed


def add_bibid(desc, bibid):
    """Add BIBID to a description

    Args:
        desc (str): Book description
        bibid (int): bibid

    Returns:
        str: modified description text
    """
    clio_link = "<p><a href='https://clio.columbia.edu/catalog/{}'>Go to catalog record in CLIO.</a></p>".format(
        str(bibid))
    return "<p>" + desc + "</p>" + clio_link


def get_bibid(docid, lookup=BIBID_LOOKUP_PATH):
    """Look up bibid based on lookup table.

    Args:
        docid (int): Proquest docid
        lookup (uri, optional): Local path to lookup table. Defaults to BIBID_LOOKUP_PATH JSON file.

    Returns:
        int: BIBID
    """
    with open(lookup, "rb") as f:
        lookup_data = json.load(f)
    return next((item['bibid'] for item in lookup_data
                 if item["docid"] == str(docid)), None)


def get_type(links_data):
    """Determines which binary book types are available

    Args:
        links_data (dict): dict representation of 'links' object in feed data

    Returns:
        dict: dict of form {'has_pdf': <boolean>, 'has_epub': <boolean>}
    """
    res = {'has_pdf': False, 'has_epub': False}
    for item in links_data:
        if item['type'] == "application/pdf":
            res['has_pdf'] = True
        if item['type'] == "application/epub+zip":
            res['has_epub'] = True
        if item['type'] == "application/vnd.adobe.adept+xml":
            res['has_pdf'] = res['has_epub'] = True

    return (res)


if __name__ == "__main__":
    main()
