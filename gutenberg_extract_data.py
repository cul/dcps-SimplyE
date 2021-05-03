# TODO: Notes

import dcps_utils as util
import requests
import json
from sheetFeeder import dataSheet
from pprint import pprint
from datetime import datetime
import re
from lxml import etree
import os.path
from opds_validate import validate_files


def main():

    # x = get_oapen_item(627426)
    # pprint(x)

    xml_dir = '/Users/dwh2128/Documents/SimplyE/books/Gutenberg/epub/'

    xslt_path = '/Users/dwh2128/Documents/SimplyE/books/Gutenberg/gutenberg_to_opds.xsl'

    output_folder = 'output/oa_clio/aaw/'

    sheet_id = '1aS2zZzDOAzr-LwNGjhxEofIfLBWIO0XM2Ft43Ec1amo'

    sheet_tab = 'AAW'
    # sheet_tab = 'Sheet1'
    # sheet_tab = 'Test'
    feed_stem = 'gutenberg_feed'
    collection_title = "Project Gutenberg EBooks | Columbia University Libraries"
    print('Extracting ' + sheet_tab + ' ... ')

    the_info = get_collection(sheet_id, sheet_tab, feed_stem,
                              collection_title, multipart=False)

    # Divide list into chunks

    # chunk_size = 5
    chunk_size = 500
    total_count = len(the_info)
    print('Total count: ' + str(total_count))
    running_count = 0
    the_chunks = divide_list(the_info, chunk_size)

    for idx, record_chunk in enumerate(the_chunks):

        running_count += len(record_chunk)
        print('Running_count = ' + str(running_count))
        print('')
        page_no = idx + 1
        if page_no > 1:
            feed_name = feed_stem + '_p' + str(page_no) + '.xml'
            feed_list_name = feed_stem + '_list_p' + str(page_no) + '.xml'
        else:
            feed_name = feed_stem + '.xml'
            feed_list_name = feed_stem + '_list' + '.xml'

        # Add feed_next, only if it is not the last one
        if running_count < total_count:
            feed_next_name = feed_stem + '_p' + str(page_no + 1) + '.xml'
            feed_next_path = 'https://ebooks.library.columbia.edu/static-feeds/oa_clio/' + feed_next_name
        else:
            feed_next_name = ''
            feed_next_path = ''

        root = etree.Element("records")
        for r in record_chunk:
            rdf_path = xml_dir + str(r['id']) + '/pg' + str(r['id']) + '.rdf'
            # Look to verify that there is an RDF file to get data from.
            if os.path.exists(rdf_path):

                rec = etree.SubElement(root, "record")
                bibid = etree.SubElement(rec, "bibid")
                bibid.text = r['bibid']
                bookid = etree.SubElement(rec, "bookid")
                bookid.text = r['id']
            else:
                print("Warning: could not find RDF file for " + str(r['id']))

        # print(etree.tostring(root, pretty_print=True))
        list_file_path = 'output/' + feed_list_name
        with open(list_file_path, 'wb') as f:
            f.write(etree.tostring(root, pretty_print=True))

        # feed_file_name = feed_stem + '.xml'

        util.saxon_process(
            list_file_path, xslt_path, output_folder + feed_name,
            theParams='feedURL=https://ebooks.library.columbia.edu/static-feeds/oa_clio/' + feed_name + ' feedNext=' + feed_next_path)

    val = validate_files(output_folder)

    the_errors = [f for f in val if f['errors']]
    if the_errors:
        print(the_errors)
    else:
        print("All files are valid!")

    quit()


def get_collection(sheet_id, sheet_tab,
                   feed_stem, collection_title, multipart=False):

    the_in_sheet = dataSheet(sheet_id, sheet_tab + '!A:Z')
    the_out_sheet = dataSheet(sheet_id, 'extract-errors!A:Z')

    # get a list of bibids and ia ids to process
    the_inputs = the_in_sheet.getData()
    the_inputs.pop(0)  # remove head row
    the_records = []
    for i in the_inputs:
        the_920s = i[4].split(';')  # get arbitrary number of 920s for this row
        rl = []
        for r in the_920s:
            if 'www.gutenberg.org/ebooks/' in r:
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

    # feed_data = extract_data(the_records, feed_stem, collection_title)
    return the_records


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
    p = re.compile('.*\$[ua]http.*?www\.gutenberg\.org/ebooks/(\d+)(;|\$|$)')
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
    dupe_errors = [[feed_stem, r['bibid'], r['id'], 'Duplicate ID']
                   for r in records if r['id'] in dupe_ids]
    # pprint(dupe_errors)
    the_errors += dupe_errors

    for record in records:
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
