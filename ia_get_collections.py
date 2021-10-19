# Script to gather ids and bibids for AI assets linked from CLIO,
# harvest metadata from IA, and save in a pickled data file.
# This data then gets used to build an OPDS feed in the next
# step in workflow.

# internet archive python library docs:
# https://archive.org/services/docs/api/internetarchive/

# from pprint import pprint
import ia_opds_functions as ia
from sheetFeeder import dataSheet
import dcps_utils as util

# If True, use output_test directory, to sync to test server
TEST = True


# SHEET_ID = '1yTDyd5GQFEsVBiKOnt5T1ejBdXhxhmXVUn6jQ-dg_5I'
SHEET_ID = '1sQBo05FvQ8Z6Yi-shBWRHYdgDgjQPdD2SgP-6-NigGg'

OUT_PATH = 'output_test/ia/' if TEST else 'output/ia/'


def main():
    """Script to gather ids and bibids for AI assets linked from CLIO,
harvest metadata from IA, and save in pickled data files.
This data then gets used to build an OPDS feed in the next
step in workflow. Run this to extract the listed collections.
Relies on Google sheet with one collection per tab.
    """

    collections_info = [
        {
            'sheet_tab': 'AveryTrade',
            'feed_stem': 'ia_avt_feed',
            'collection_title': 'Avery Library Architectural Trade Catalogs'
        },
        {
            'sheet_tab': '965carnegiedpf',
            'feed_stem': 'ia_ccny_feed',
            'collection_title': 'Carnegie Corporation of New York'
        },
        {
            'sheet_tab': 'Durst',
            'feed_stem': 'ia_durst_feed',
            'collection_title': 'Seymour B. Durst Old York Library'
        },
        {
            'sheet_tab': 'HebrewMSS',
            'feed_stem': 'ia_hebrewmss_feed',
            'collection_title': "Hebrew Manuscripts"
        },
        {
            'sheet_tab': 'MedicalHeritage',
            'feed_stem': 'ia_med_feed',
            'collection_title': 'Medical Heritage Library'
        },
        {
            'sheet_tab': 'Missionary',
            'feed_stem': 'ia_mrp_feed',
            'collection_title': 'Missionary Research Pamphlets'
        },
        {
            'sheet_tab': 'MWM',
            'feed_stem': 'ia_mwm_feed',
            'collection_title': "Muslim World Manuscripts"
        },
        {
            'sheet_tab': 'WWI',
            'feed_stem': 'ia_wwi_feed',
            'collection_title': 'WWI Pamphlets 1913-1920'
        },

    ]

    for c in collections_info:
        pickle_collection(c['sheet_tab'], c['feed_stem'],
                          c['collection_title'])

    quit()


def pickle_collection(sheet_tab, feed_stem, collection_title):
    """Save an IA collection in a pickle file.

    Args:
        sheet_tab (str): sheet tab name
        feed_stem (str): feed stem
        collection_title (str): collection title
    """
    print('Extracting ' + sheet_tab + ' ... ')
    get_collection(SHEET_ID, sheet_tab, feed_stem,
                   collection_title, multipart=False)


def get_collection(sheet_id, sheet_tab,
                   feed_stem, collection_title, multipart=False):
    """Get Internet Archive collection and save to pickle.

    Args:
        sheet_id (str): Google sheet id
        sheet_tab (str): Google sheet tab name
        feed_stem (str): abbreviation to be used in file naming and feed identification
        collection_title (str): Title of collection (e.g., Medical Heritage Library)
        multipart (bool, optional): Incl/exclude multi-volume works. Defaults to False.
    """
    the_in_sheet = dataSheet(sheet_id, sheet_tab + '!A:Z')
    the_out_sheet = dataSheet(sheet_id, 'extract-errors!A:Z')

    pickle_path = OUT_PATH + feed_stem + '.pickle'

    # get a list of bibids and ia ids to process
    the_inputs = the_in_sheet.getData()
    the_inputs.pop(0)  # remove head row
    print(str(len(the_inputs)) + ' records in ' + collection_title + '...')
    the_records = []
    for i in the_inputs:

        # the_920s = i[6:]  # get arbitrary number of 920s for this row
        the_920s = i[4].split(';')  # get arbitrary number of 920s for this row
        rl = []
        for r in the_920s:
            if 'archive.org' in r:
                rp = ia.parse_920(r)
                # Only add if id != None.
                if bool(rp['id']):
                    rl.append(
                        {'bibid': i[0], 'id': rp['id'], 'label': rp['label']})

        # If we are allowing multi-volume works, add all;
        # otherwise, only add to list if it is a monograph.
        if len(rl) == 1 or multipart is True:
            the_records += rl

    feed_data = ia.extract_data(the_records, feed_stem, collection_title)

    print('Saving ' + str(len(feed_data['data'])
                          ) + ' records to ' + pickle_path)
    util.pickle_it(feed_data, pickle_path)

    the_out_sheet.appendData(feed_data['errors'])

    # fin


if __name__ == "__main__":
    main()
