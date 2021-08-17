import json
import os
from pprint import pprint
import dcps_utils as util


MY_PATH = os.path.dirname(__file__)

BIBID_LOOKUP_PATH = os.path.join(
    MY_PATH, "output_test/proquest/proquest_lookup.json")

FEED_URL = os.path.join(
    MY_PATH, "output_test/proquest/ProQuest_BooksCatalog.json")

EPUB_OUT_PATH = os.path.join(
    MY_PATH, "output_test/proquest/proquest_books_catalog_epub.json")

PDF_OUT_PATH = os.path.join(
    MY_PATH, "output_test/proquest/proquest_books_catalog_pdf.json")


def main():

    epub_opds = build_proquest_opds(
        FEED_URL, EPUB_OUT_PATH, feed_type="epub")

    api_response = api_wrap(epub_opds)

    print("Saving " + str(len(epub_opds['publications'])) +
          " records to " + str(EPUB_OUT_PATH) + "...")
    with open(EPUB_OUT_PATH, "w") as f:
        json.dump(api_response, f)

    quit()
    build_proquest_opds(FEED_URL, PDF_OUT_PATH, feed_type="pdf")

    with open(FEED_URL, "rb") as f:
        json_data = json.load(f)

    the_books = json_data['opdsFeed']['groups'][0]['publications']

    out_data = []
    for b in the_books:
        docid = b['metadata']['identifier'].split('/')[-1]
        bibid = get_bibid(docid)
        if not bibid:
            # There is no catalog record; skip this one
            continue
        link_info = get_type(b['links'])
        if link_info['has_epub']:
            if 'description' not in b['metadata']:
                b['metadata']['description'] = ''
            b['metadata']['description'] = add_bibid(
                b['metadata']['description'], bibid)
            out_data.append(b)
    for i in out_data:
        print(i['metadata']['identifier'])
        print(i['metadata']['description'])

    print("Saving " + str(len(out_data)) +
          " records to " + str(EPUB_OUT_PATH) + "...")
    with open(EPUB_OUT_PATH, "w") as f:
        json.dump(out_data, f)

    quit()


def api_wrap(opds_feed):
    # Take the OPDS data and wrap in the custom ProQuest API response.
    return {
        "status": "Success",
        "statusCode": 200,
        "statusMsg": "OK",
        "opdsFeed": opds_feed
    }


def build_proquest_opds(feed_url, out_path, feed_type="all"):
    with open(feed_url, "rb") as f:
        json_data = json.load(f)

    the_books = json_data['opdsFeed']['groups'][0]['publications']

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


def add_bibid(desc, bibid, lookup=BIBID_LOOKUP_PATH):
    clio_link = "<p><a href='https://clio.columbia.edu/catalog/{}'>Go to catalog record in CLIO.</a></p>".format(
        str(bibid))
    return "<p>" + desc + "</p>" + clio_link


def get_bibid(docid, lookup=BIBID_LOOKUP_PATH):
    with open(lookup, "rb") as f:
        lookup_data = json.load(f)
    return next((item['bibid'] for item in lookup_data
                 if item["docid"] == str(docid)), None)


def get_type(links_data):
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
