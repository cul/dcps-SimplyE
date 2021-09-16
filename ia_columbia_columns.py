# Get IA collection specific to serial (Columbia Library Columns).

import re
import ia_opds_functions as ia
from sheetFeeder import dataSheet
from pprint import pprint
import dcps_utils as util


def main():
    """Get IA collection specific to serial (Columbia Library Columns).
    """
    sheet_id = '1yTDyd5GQFEsVBiKOnt5T1ejBdXhxhmXVUn6jQ-dg_5I'
    sheet_tab = 'ColumbiaColumns'
    the_in_sheet = dataSheet(sheet_id, sheet_tab + '!A:Z')
    the_out_sheet = dataSheet(sheet_id, 'extract-errors!A:Z')
    the_err_sheet = dataSheet(sheet_id, 'errors!A:Z')

    output_folder = 'output/ia/'
    feed_stem = 'ia_clc_feed'
    collection_title = 'Columbia Library Columns'
    abbr = 'clc'

    pickle_path = output_folder + feed_stem + '.pickle'

    the_input = the_in_sheet.getData()
    heads = the_input.pop(0)

    the_records = [{'bibid': r[0], 'id':r[2], 'label': r[3]}
                   for r in the_input]

    feed_data = ia.extract_data(the_records, feed_stem, collection_title)

    feed_data_new = {'errors': feed_data['errors'], 'data': []}
    for e in feed_data['data']:
        new_entry = e

        des = new_entry['description']
        des_new = []
        for d in des:
            if '<a' not in d:
                des_new.append(d)
        new_entry['description'] = des_new
        feed_data_new['data'].append(new_entry)

    # pprint(feed_data_new)

    # Save to pickle.
    print('Saving ' + str(len(feed_data_new['data'])
                          ) + ' records to ' + pickle_path)
    # util.pickle_it(feed_data_new['data'], pickle_path)
    util.pickle_it(feed_data_new, pickle_path)

    # Report any extraction errors

    the_out_sheet.appendData(feed_data['errors'])

    # Generate XML

    x = ia.build_feed(output_folder + feed_stem + '.pickle', abbr)

    # report any build errors/warnings
    the_err_sheet.appendData(x)

    # fin


if __name__ == "__main__":
    main()
