# Report data from ProQuest feed. Uses local copy of feed data.
import json
import os
from pprint import pprint
from sheetFeeder import dataSheet
import dcps_utils as util


MY_PATH = os.path.dirname(__file__)


def main():

    sheet_id = '1_1d8aElm9yRG4Avy9j6WxTh2TjhMp8iqaeZkgUNdxeE'
    report_sheet = dataSheet(sheet_id, 'Test!A:Z')
    lookup_sheet = dataSheet(sheet_id, 'Lookup!A:Z')

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


def report_from_feed(feed_url, data_sheet):

    with open(feed_url, "rb") as f:
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
