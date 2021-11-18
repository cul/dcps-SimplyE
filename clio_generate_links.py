# Script to output bibid and URLs for creating links from CLIO to SimplyE.
# Output is a CSV to upload to /cul/cul0/ldpd/simplye/clio_links/, plus
# more complete tabular data loaded into sheet for Data Studio reports.
# Data sources are :
# 1. OPDS XML files in a given directory tree
# 2. ONIX XML files in a given directory tree.


import dcps_utils as util
import os
from sheetFeeder import dataSheet
import csv
from itertools import groupby
import json
import proquest_get_info

MY_PATH = os.path.dirname(os.path.abspath(__file__))

TEST = True

SHEET_ID = '1r8oaOQT955HvAii-5sF3IDwXR1_SGXx_KZRLN40JK9s'
SHEET_TAB = 'Test' if TEST else 'Data'
OUTPUT_DIR = 'output_test' if TEST else 'output'
SITE = 'https://ebooks.lyrasistechnology.org/columbia' if TEST else 'https://academic.lyrasistechnology.org/columbia'

# GSheet for reporting output
OUT_SHEET = dataSheet(SHEET_ID, SHEET_TAB + '!A:Z')

# Locations of things
CSV_OUT_PATH = os.path.join(
    MY_PATH, OUTPUT_DIR + '/clio_links/simplye_clio_links.csv')
OPDS_DIR = os.path.join(
    MY_PATH,  OUTPUT_DIR + '/')
ONIX_DIR = os.path.join(MY_PATH, 'onix')

OPDS_XSLT = os.path.join(MY_PATH, 'xslt/opds_clio_csv.xsl')
ONIX_XSLT = os.path.join(MY_PATH, 'xslt/onix_clio_csv.xsl')

# other constants
ONIX_COLLS = [
    {'dir': 'JHU', 'name': 'Johns Hopkins University Press'},
    {'dir': 'Casalini', 'name': 'Casalini'}
]

# ProQuest stuff
PQ_VENDOR = "ProQuest"
PQ_COLLECTION = "ProQuest"

PQ_URL_FORMAT = SITE + "/book/https%3A%2F%2Fdemo.lyrasistechnology.org%2Fcolumbia%2Fworks%2FProQuest%2520Doc%2520ID%2F" if TEST else SITE + \
    "/book/https%3A%2F%2Facademic.lyrasistechnology.org%2Fcolumbia%2Fworks%2FProQuest%2520Doc%2520ID%2F"

# Serials that get special treatment in CSV bc they are not 1:1
# (LingLong, CLC)
# THE_SERIALS = ['6309312', '11500540']
THE_SERIALS = [
    {'bibid': '6309312', 'path': '/collection/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Ffeed%2F175%3Fentrypoint%3DBook'},
    {'bibid': '11500540', 'path': '/collection/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Fgroups%2F176%3Fentrypoint%3DBook'}
]


def main():
    """Script to output bibid and URLs for creating links from CLIO to SimplyE.
Output is a CSV to upload to /cul/cul0/ldpd/simplye/clio_links/, plus
more complete tabular data loaded into Google sheet for Data Studio reports.
Data sources are :
1. OPDS XML files in a given directory tree
2. ONIX XML files in a given directory tree
3. ProQuest OPDS 2.0 JSON feed file given directory tree
    """

    sheet_output = []  # this will contain the combined output

    print("")
    print('*** Getting OPDS v1.2 XML data ... ***')
    print("")

    params = "file_path=" + OPDS_DIR + " site=" + SITE
    opds_data = util.xml_to_array(OPDS_XSLT, OPDS_XSLT, params=params)

    print(str(len(opds_data)) + " records found in OPDS XML.")
    sheet_output += opds_data

    print("")
    print('*** Getting ONIX data ... ***')
    print("")

    for coll in ONIX_COLLS:
        params = ("input_dir='" +
                  str(os.path.join(MY_PATH, ONIX_DIR, coll['dir'])) +
                  "' publisher='" +
                  coll['name'] +
                  "'")
        onix_data = util.xml_to_array(ONIX_XSLT, ONIX_XSLT, params=params)
        onix_data.pop(0)  # remove heads
        sheet_output += onix_data

        print(str(len(onix_data)) + " records found in " + coll['name'])

    print("")
    print('*** Getting ProQuest data ... ***')
    print("")

    print('Saving latest ProQuest data in ' + os.path.join(
        MY_PATH, OUTPUT_DIR + '/proquest/'))
    # Extract the data. Requires proxy if not in whitelist.
    proquest_get_info.get_proquest_feed()

    pq_output = []

    pq_filepath = os.path.join(
        MY_PATH, OUTPUT_DIR, "proquest/ProQuest_BooksCatalog.json")
    pq_lookup = os.path.join(
        MY_PATH, OUTPUT_DIR, "proquest/proquest_lookup.json")

    with open(pq_filepath, "rb") as f:
        json_data = json.load(f)
    the_books = json_data['opdsFeed']['groups'][0]['publications']

    with open(pq_lookup, "rb") as f:
        lookup_data = json.load(f)

    for b in the_books:
        docid = b['metadata']['identifier'].split('/')[-1]
        # Check if docid is in lookup
        bibid = find_in_lookup(lookup_data, "docid", docid, "bibid")
        if bibid:
            url = PQ_URL_FORMAT + docid
            title = b['metadata']['title']
            id = b['metadata']['identifier']
            link_info = proquest_get_info.get_type(b['links'])
            has_pdf = "Y" if link_info['has_pdf'] else None
            has_epub = "Y" if link_info['has_epub'] else None

            # Capture a row of data
            pq_output.append([bibid, PQ_VENDOR, PQ_COLLECTION,
                              title, id, url, has_pdf, has_epub])

    print(str(len(pq_output)) + " records found in ProQuest.")
    sheet_output += pq_output

    # Post complete data to sheet
    OUT_SHEET.clear()
    OUT_SHEET.appendData(sheet_output)

    print("")
    print("Report data in " + OUT_SHEET.url)
    print("")

    # For CSV, trim out all but cols 0 and 5 (bibid and id)
    csv_output = util.trim_array(sheet_output, [1, 2, 3, 4, 6, 7])
    csv_heads = csv_output.pop(0)

    # remove serials from csv (not one-to-one, treated separately)
    csv_output_clean = [r for r in util.sort_array(csv_output)
                        if str(r[0]) not in [r['bibid'] for r in THE_SERIALS]]
    # add in LingLong and CLC lookup
    csv_output_clean += [[r['bibid'], SITE + r['path']] for r in THE_SERIALS]
    csv_output_clean.insert(0, csv_heads)

    with open(CSV_OUT_PATH, mode='w') as f:
        w = csv.writer(f, delimiter=',', quotechar='"',
                       quoting=csv.QUOTE_MINIMAL)
        w.writerows(csv_output_clean)

    print("")
    print("Updated CSV in " + CSV_OUT_PATH)
    print("")
    print("Done!")


# ! No longer needed, done in XSLT!
def merge_booleans(data, cols, match_key=0):
    # Intended to merge 2 ONIX records per book, combining
    # PDF and EPUB booleans. Format must be 'Y'/''.
    # Use: data = array with UID (bibid) and some booleans;
    # cols = list of col indexes, e.g.,  [4,5]
    # match_key is the UID to group by, e.g., BIBID.
    # Returns sorted list with only one row per UID and merged
    # booleans.
    new_data = []
    data_sorted = util.sort_array(data)  # sort by BIBID
    # Group duplicate ids together using itertools.groupby
    for key, group in groupby(data_sorted, lambda x: x[match_key]):
        # print(key)
        combined = list(group)
        new_row = combined[0]
        for c in cols:
            c_slice = [r[c] for r in combined]
            if 'Y' in c_slice:
                new_row[c] = "Y"
        new_data.append(new_row)
    return new_data


def find_in_lookup(list, key, value, return_key):
    for i in list:
        if i[key] == value:
            return i[return_key]


if __name__ == "__main__":
    main()
