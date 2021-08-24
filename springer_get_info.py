# Report data from Springer data store
import json
import os
from pprint import pprint
from sheetFeeder import dataSheet


MY_PATH = os.path.dirname(__file__)


def main():

    the_sheet = dataSheet(
        '183S8_aMD6py8XvVzIAE4WnDyUeCuLYsyacyNImX1frM', 'Sheet1!A:Z')

    in_file = os.path.join(
        MY_PATH, "output_test/springer/springer_test_feed_datastore.json")

    with open(in_file, "rb") as f:
        json_data = json.load(f)

    the_data = [['Title', 'DOI', 'ISBN',
                 'Print ISBN', 'E-ISBN', 'Pub Date', 'PDF', 'EPUB']]
    for b in json_data:
        title = b['publicationName']
        doi = b['doi']
        isbn = b['isbn']
        print_isbn = b['printIsbn']
        e_isbn = b['electronicIsbn']
        pub_date = b['publicationDate']

        link_info = get_type(b)

        row = [title, doi, isbn, print_isbn, e_isbn, pub_date,
               link_info['has_pdf'], link_info['has_epub']]
        # print(get_type(b['links']))
        the_data.append(row)

    the_sheet.clear()
    the_sheet.appendData(the_data)
    quit()


def get_type(record):
    res = {'has_pdf': False, 'has_epub': False}
    if 'ePubUrl' in record:
        res['has_epub'] = True
    for item in record['url']:
        if item['format'] == "pdf":
            res['has_pdf'] = True
    return (res)


if __name__ == "__main__":
    main()
