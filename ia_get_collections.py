# Script to gather ids and bibids for AI assets linked from CLIO, harvest metadata from IA, and save in a pickled data file. This data then gets used to build an OPDS feed in the next step in workflow.

# internet archive python library docs:
# https://archive.org/services/docs/api/internetarchive/

import dcps_utils as util
from sheetFeeder import dataSheet
import ia_opds_functions as ia


def main():

    # Run this to extract all of the collections below.

    sheet_id = '1yTDyd5GQFEsVBiKOnt5T1ejBdXhxhmXVUn6jQ-dg_5I'

    sheet_tab = 'HebrewMSS'
    feed_stem = 'ia_hebrewmss_feed'
    collection_title = "Hebrew Manuscripts"
    print('Extracting ' + sheet_tab + ' ... ')
    get_collection(sheet_id, sheet_tab, feed_stem,
                   collection_title, multipart=False)

    quit()


    sheet_tab = '965carnegiedpf'
    feed_stem = 'ia_ccny_feed'
    collection_title = "Carnegie Corporation of New York"
    print('Extracting ' + sheet_tab + ' ... ')
    get_collection(sheet_id, sheet_tab, feed_stem,
                   collection_title, multipart=False)

    sheet_tab = 'MWM'
    feed_stem = 'ia_mwm_feed'
    collection_title = "Muslim World Manuscripts"
    print('Extracting ' + sheet_tab + ' ... ')
    get_collection(sheet_id, sheet_tab, feed_stem,
                   collection_title, multipart=False)

    sheet_tab = 'AveryTrade'
    feed_stem = 'ia_avt_feed'
    collection_title = "Avery Library Architectural Trade Catalogs"
    print('Extracting ' + sheet_tab + ' ... ')
    get_collection(sheet_id, sheet_tab, feed_stem,
                   collection_title, multipart=False)

    sheet_tab = 'Missionary'
    feed_stem = 'ia_mrp_feed'
    collection_title = "Missionary Research Pamphlets"
    print('Extracting ' + sheet_tab + ' ... ')
    get_collection(sheet_id, sheet_tab, feed_stem,
                   collection_title, multipart=False)

    sheet_tab = 'Durst'
    feed_stem = 'ia_durst_feed'
    collection_title = "Seymour B. Durst Old York Library"
    print('Extracting ' + sheet_tab + ' ... ')
    get_collection(sheet_id, sheet_tab, feed_stem,
                   collection_title, multipart=False)

    sheet_tab = 'MedicalHeritage'
    feed_stem = 'ia_med_feed'
    collection_title = "Medical Heritage Library"
    print('Extracting ' + sheet_tab + ' ... ')
    get_collection(sheet_id, sheet_tab, feed_stem,
                   collection_title, multipart=False)

    sheet_tab = 'WWI'
    feed_stem = 'ia_wwi_feed'
    collection_title = "WWI Pamphlets 1913-1920"
    print('Extracting ' + sheet_tab + ' ... ')
    get_collection(sheet_id, sheet_tab, feed_stem,
                   collection_title, multipart=False)

    quit()


def get_collection(sheet_id, sheet_tab,
                   feed_stem, collection_title, multipart=False):

    the_in_sheet = dataSheet(sheet_id, sheet_tab + '!A:Z')
    the_out_sheet = dataSheet(sheet_id, 'extract-errors!A:Z')

    pickle_path = 'output/ia/' + feed_stem + '.pickle'

    # get a list of bibids and ia ids to process
    the_inputs = the_in_sheet.getData()
    the_inputs.pop(0)  # remove head row
    the_records = []
    for i in the_inputs:

        # the_920s = i[6:]  # get arbitrary number of 920s for this row
        the_920s = i[4].split(';')  # get arbitrary number of 920s for this row
        rl = []
        for r in the_920s:
            if 'archive.org' in r:
                rp = ia.parse_920(r)
                rl.append(
                    {'bibid': i[0], 'id': rp['id'], 'label': rp['label']})

        # If we are allowing multi-volume works, add all;
        # otherwise, only add to list if it is a monograph.
        if len(rl) == 1 or multipart is True:
            the_records += rl

    # print(the_records)

    feed_data = ia.extract_data(the_records, feed_stem, collection_title)

    print('Saving ' + str(len(feed_data['data'])
                          ) + ' records to ' + pickle_path)
    util.pickle_it(feed_data['data'], pickle_path)

    # pprint(feed_data['data'])
    # pprint(feed_data['errors'])

    the_out_sheet.appendData(feed_data['errors'])

    # fin


if __name__ == "__main__":
    main()
