# Script to harvest data from the OAPEN api (library.oapen.org/rest) for use in composing OPDS feed. The list of ids is obtained from a spreadsheet (cols 6 or 7 in this case). The ids are queried using dc.identifier parameter.
#
# Example query:
# https://library.oapen.org/rest/search?query=dc.identifier:627426&expand=metadata,bitstreams,parentCollection
#
# The script also merges an ILS BIBID (id[0]) into the output for later use
# in linking back to catalog.
# Result is a pickled dictionary. This is in turn read by another script
# (oapen_build_opds) to build OPDS XML file(s).


import dcps_utils as util
import requests
import json
from sheetFeeder import dataSheet
from pprint import pprint
from datetime import datetime
import re


def main():

    # x = get_oapen_item(627426)
    # pprint(x)

    sheet_id = '1kLI8x1whzSNqeKL5xVysopgKYWE9-D9H_PHX2RkW4wQ'

    # sheet_tab = 'Test2'  # test
    sheet_tab = 'ingest'
    feed_stem = 'oapen_clio'
    collection_title = "OAPEN Book Collection | Columbia University Libraries"
    print('Extracting ' + sheet_tab + ' ... ')
    get_collection(sheet_id, sheet_tab, feed_stem,
                   collection_title, multipart=False)

    quit()


def get_collection(sheet_id, sheet_tab,
                   feed_stem, collection_title, multipart=False):

    the_in_sheet = dataSheet(sheet_id, sheet_tab + '!A:Z')
    the_out_sheet = dataSheet(sheet_id, 'extract-errors!A:Z')

    pickle_path = 'output/oapen/' + feed_stem + '.pickle'

    # get a list of bibids and ia ids to process
    the_inputs = the_in_sheet.getData()
    the_inputs.pop(0)  # remove head row
    the_records = []
    for i in the_inputs:
        the_920s = i[4].split(';')  # get arbitrary number of 920s for this row
        rl = []
        for r in the_920s:
            # if 'oapen.org/record' in r:
            if 'library.oapen.org/handle/20.500.12657/' in r:
                rp = parse_920(r)
                rl.append(
                    {'bibid': i[0], 'id': rp['id'], 'label': rp['label']})

        # If we are allowing multi-volume works, add all;
        # otherwise, only add to list if it is a monograph.
        if len(rl) == 1 or multipart is True:
            the_records += rl
        elif len(rl) > 1:
            print("WARNING: " + str(i[0]) + " has multiple volumes. Skipping!")
        else:
            print("WARNING: could not find OAPEN record in " +
                  str(i[0]) + ". Skipping!")

    feed_data = extract_data(the_records, feed_stem, collection_title)

    print('Saving ' + str(len(feed_data['data'])
                          ) + ' records to ' + pickle_path)
    util.pickle_it(feed_data, pickle_path)

    # print(feed_data['data'])
    pprint(feed_data['errors'])

    the_out_sheet.appendData(feed_data['errors'])

    # fin


def get_oapen_item(_id):
    base_url = 'https://library.oapen.org/rest/search'
    # query = base_url + '?query=dc.identifier:' + \
    #     str(_id) + '&expand=metadata,bitstreams,parentCollection'
    query = base_url + '?query=dc.identifier.uri:' + \
        str(_id) + '&expand=metadata,bitstreams,parentCollection'
    r = requests.get(query)
    r.encoding = 'UTF-8'
    return json.loads(r.text)


def divide_list(lst, n):
    # generate n-sized chunks from list.
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def parse_920(_str):
    # Parse a string and extract the $3 subfield
    # as ['label'] and $u or $a as ['id']
    results = {}
    p = re.compile('\$[3z](.*?)(;|\$|$)')
    match_label = p.match(_str)
    results['label'] = match_label.group(1) if match_label else None
    # p = re.compile('.*\$[ua]http.*?oapen\.org/record/(\d+)(;|\$|$)')
    p = re.compile(
        '.*\$[ua]https?\S*?oapen\.org/handle/20\.500\.12657/(\d+)(;|\$|$)')
    match_id = p.match(_str)
    results['id'] = match_id.group(1) if match_id else None
    return results


def extract_data(records, feed_stem, collection_title):
    # records is list of dicts of form:
    #     {'bibid': <bibid>, 'id':<ia_id>, 'label':<link_label>}
    # feed_stem is the label that will be used to name XML files, e.g.:
    #    'ia_mrp_feed'
    # collection_title is a human-readable string, e.g.:
    #    "Missionary Research Pamphlets"

    the_output = []
    the_errors = []

    # check for duplicate ids and report them (they will be processed anyway)
    the_ids = [r['id'] for r in records]
    print(the_ids)
    dupe_ids = find_duplicates(the_ids)
    dupe_errors = [[str(datetime.today()), feed_stem, r['bibid'], r['id'], 'Duplicate ID']
                   for r in records if r['id'] in dupe_ids]
    # pprint(dupe_errors)
    the_errors += dupe_errors

    for record in records:
        print(record['bibid'])
        print(record['id'])

        # record_metadata = get_item(record['id']).metadata

        record_metadata = get_oapen_item(record['id'])
        if len(record_metadata) != 1:
            # no entries returned, or more than one (!) returned.
            print('Either no data or multiple matches for ' +
                  record['id'] + '. Skipping...')

            the_errors.append(
                [feed_stem, record['bibid'], record['id'], 'Either no data or multiple matches!'])

        else:

            record_metadata[0]['cul_metadata'] = {'bibid': record['bibid'],
                                                  'feed_id': feed_stem,
                                                  'collection_name':
                                                  collection_title,
                                                  'label': record['label']}

            the_output.append(record_metadata[0])

    return {'data': the_output, 'errors': the_errors}


def find_duplicates(lst):
    unique = []
    dupes = []
    for i in lst:
        if i not in unique:
            unique.append(i)
        else:
            dupes.append(i)
    return list(set(dupes))


if __name__ == '__main__':
    main()
