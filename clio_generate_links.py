# Script to output bibid and URLs for creating links from CLIO to SimplyE.
# Output is a CSV to upload to /cul/cul0/ldpd/simplye/clio_links/, plus
# more complete tabular data loaded into sheet for Data Studio reports.
# Data sources are :
# 1. OPDS XML files in a given directory tree
# 2. ONIX XML files in a given directory tree.


from posixpath import join
import dcps_utils as util
import os
from sheetFeeder import dataSheet
import csv
from itertools import groupby

MY_PATH = os.path.dirname(__file__)

TEST = True

SHEET_ID = '1r8oaOQT955HvAii-5sF3IDwXR1_SGXx_KZRLN40JK9s'
SHEET_TAB = 'Test' if TEST else 'Data'
OUTPUT_DIR = 'output_test' if TEST else 'output'
SITE = 'https://ebooks.lyrasistechnology.org/columbia' if TEST else 'https://academic.lyrasistechnology.org/columbia'


def main():
    """Script to output bibid and URLs for creating links from CLIO to SimplyE.
Output is a CSV to upload to /cul/cul0/ldpd/simplye/clio_links/, plus
more complete tabular data loaded into Google sheet for Data Studio reports.
Data sources are :
1. OPDS XML files in a given directory tree
2. ONIX XML files in a given directory tree.
    """

    CSV_OUT_PATH = os.path.join(
        MY_PATH, OUTPUT_DIR + '/clio_links/simplye_clio_links.csv')

    OUT_SHEET = dataSheet(SHEET_ID, SHEET_TAB + '!A:Z')

    OPDS_DIR = os.path.join(
        MY_PATH,  OUTPUT_DIR + '/')
    print(OPDS_DIR)
    ONIX_DIR = 'onix'
    ONIX_COLLS = [
        {'dir': 'JHU', 'name': 'Johns Hopkins University Press'},
        {'dir': 'Casalini', 'name': 'Casalini'}
    ]
    OPDS_XSLT = os.path.join(MY_PATH, 'xslt/opds_clio_csv.xsl')
    ONIX_XSLT = os.path.join(MY_PATH, 'xslt/onix_clio_csv.xsl')

    sheet_output = []  # this will contain the combined output

    print('*** Getting OPDS data ... ***')
    params = "file_path=" + OPDS_DIR + " site=" + SITE
    opds_data = util.xml_to_array(OPDS_XSLT, OPDS_XSLT, params=params)

    print(str(len(opds_data)) + " records found in OPDS.")
    sheet_output += opds_data

    print('*** Getting ONIX data ... ***')

    for coll in ONIX_COLLS:
        params = ("input_dir='" +
                  str(os.path.join(MY_PATH, ONIX_DIR, coll['dir'])) +
                  "' publisher='" +
                  coll['name'] +
                  "'")
        # print(params)
        onix_data = util.xml_to_array(ONIX_XSLT, ONIX_XSLT, params=params)
        onix_data.pop(0)  # remove heads
        sheet_output += onix_data

        print(str(len(onix_data)) + " records found in " + coll['name'])

    # Post to sheet
    OUT_SHEET.clear()
    OUT_SHEET.appendData(sheet_output)

    # For CSV, trim out all but cols 0 and 5 (bibid and id)
    csv_output = util.trim_array(sheet_output, [1, 2, 3, 4, 6, 7])
    csv_heads = csv_output.pop(0)

    # remove serials from csv (not one-to-one, treated separately)
    the_serials = ['6309312', '11500540']
    csv_output_clean = [r for r in util.sort_array(csv_output)
                        if str(r[0]) not in the_serials]
    # add in LingLong and CLC lookup
    csv_output_clean += get_ia_serials_lookups()
    csv_output_clean.insert(0, csv_heads)

    with open(CSV_OUT_PATH, mode='w') as f:
        w = csv.writer(f, delimiter=',', quotechar='"',
                       quoting=csv.QUOTE_MINIMAL)
        w.writerows(csv_output_clean)


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


def get_ia_serials_lookups():
    # Add LingLong and CLC group URLs (not items)
    return [['6309312',
             'https://academic.lyrasistechnology.org/columbia/collection/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Ffeed%2F175%3Fentrypoint%3DBook'],
            ['11500540',
                'https://academic.lyrasistechnology.org/columbia/collection/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Fgroups%2F176%3Fentrypoint%3DBook']]


if __name__ == "__main__":
    main()
