# Report data from ProQuest feed. Uses local copy of feed data.
import json
import os
from pprint import pprint
from sheetFeeder import dataSheet
import dcps_utils as util
from configparser import ConfigParser
import requests


MY_PATH = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(MY_PATH, "config.ini")
CONFIG = ConfigParser()
CONFIG.read(CONFIG_PATH)

# Get proxy url if there is one.
if "httpsProxy" in CONFIG["PROXIES"]:
    HTTPS_PROXY = CONFIG["PROXIES"]["httpsProxy"]
else:
    HTTPS_PROXY = None

BASE_URL = "https://ebookcentral.proquest.com/lib/columbia/BooksCatalog"
MAX_COUNT = 3000  # should be larger than total expected

TEST = True

OUT_DIR = os.path.join(
    MY_PATH, "output_test/proquest") if TEST else os.path.join(
        MY_PATH, "output/proquest")

PQ_FEED_PATH = os.path.join(OUT_DIR, "ProQuest_BooksCatalog.json")


def main():

    # Extract the data. Requires proxy if not in whitelist.
    get_proquest_feed()

    sheet_id = '1_1d8aElm9yRG4Avy9j6WxTh2TjhMp8iqaeZkgUNdxeE'
    report_sheet = dataSheet(sheet_id, 'Test!A:Z')  # test
    lookup_sheet = dataSheet(sheet_id, 'Lookup!A:Z')

    report_from_feed(PQ_FEED_PATH, report_sheet)

    quit()

    lookup_file = os.path.join(
        MY_PATH, "output_test/proquest/proquest_lookup.json")

    x = get_lookup(lookup_sheet, lookup_file)

    print(x)
    quit()
    in_file = os.path.join(
        MY_PATH, "output_test/proquest/ProQuest_BooksCatalog.json")

    with open(in_file, "rb") as f:
        json_data = json.load(f)

    the_books = json_data['opdsFeed']['groups'][0]['publications']

    the_data = [['Title', 'EBC ID', 'URL', 'PDF', 'EPUB']]
    for b in the_books:
        id = b['metadata']['identifier'].split('/')[-1]
        url = "https://ebookcentral.proquest.com/lib/columbia/detail.action?docID=" + \
            str(id)
        link_info = get_type(b['links'])
        row = [b['metadata']['title'], id, url,
               link_info['has_pdf'], link_info['has_epub']]
        # print(get_type(b['links']))
        the_data.append(row)

    report_sheet.clear()
    report_sheet.appendData(the_data)
    quit()


def save_json(out_path, data):
    """Save dict to JSON file

    Args:
        out_path (str): file path
        data (dict): the data to serialize as JSON
    """
    with open(out_path, 'w') as outfile:
        return json.dump(data, outfile)


def get_proquest_feed(filepath=PQ_FEED_PATH):
    """Retrieve PQ output and save as JSON file

    Args:
        filepath (str, optional): path to output file.
        Defaults to PQ_FEED_PATH.
    """
    pq_data = proquest_read_feed()
    return save_json(PQ_FEED_PATH, pq_data)


def proquest_read_feed(url=BASE_URL, max_count=MAX_COUNT):
    """Read PQ data from API.

    Args:
        url (str, optional): API url. Defaults to BASE_URL.
        max_count (int, optional): hitsPerPage param. Defaults to MAX_COUNT.

    Returns:
        dict: returned data
    """
    params = dict(hitsPerPage=max_count,
                  page=1)
    resp = requests.get(url=url, params=params, proxies={
                        "https": HTTPS_PROXY})

    return resp.json()


def get_lookup(data_sheet, out_path, head_row=True):
    # Expecting data with format: EBC ID | BIBID
    lookup_data = data_sheet.getData()
    if head_row:
        lookup_data.pop(0)
    new_data = [
        {'docid': r[0], 'bibid': r[1]}
        for r in lookup_data
        if len(r) > 1 and r[1] and r[1] != 'no record'
    ]

    # print(new_data)

    print("Saving to " + str(str(out_path)) + "...")
    with open(out_path, "w") as f:
        json.dump(new_data, f)

    # print(pickle_it(subject_data, out_path))


def report_from_feed(feed_path, data_sheet):
    """Take a saved JSON file from ProQuest feed and report info to a sheet for review.

    Args:
        feed_path (str): path to json file
        data_sheet (dataSheet): destination of report data
    """
    with open(feed_path, "rb") as f:
        json_data = json.load(f)

    the_books = json_data['opdsFeed']['groups'][0]['publications']

    the_data = [['Title', 'EBC ID', 'URL', 'PDF', 'EPUB']]
    for b in the_books:
        id = b['metadata']['identifier'].split('/')[-1]
        url = "https://ebookcentral.proquest.com/lib/columbia/detail.action?docID=" + \
            str(id)
        link_info = get_type(b['links'])
        row = [b['metadata']['title'], id, url,
               link_info['has_pdf'], link_info['has_epub']]
        the_data.append(row)

    data_sheet.clear()
    data_sheet.appendData(the_data)


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
