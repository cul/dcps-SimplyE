# Script to output bibid and URLs for creating links from CLIO to SimplyE for OAPEN content.
import dcps_utils as util
import os
from sheetFeeder import dataSheet

my_path = os.path.dirname(__file__)


def main():

    # x = util.unpickle_it('output/oapen/oapen_clio.pickle')

    # from pprint import pprint
    # pprint(x[1])

    report_metadata('1kLI8x1whzSNqeKL5xVysopgKYWE9-D9H_PHX2RkW4wQ',
                    'output!A:Z', 'output/oapen/oapen_clio.pickle')

    quit()
    out_sheet = dataSheet(
        '1OG0UgqHCdAzx326JNy7akx9-MOwR9A_MSf-MEv9k3Ms', 'OAPEN!A:Z')

    the_pickles = [
        'output/oapen/oapen_clio.pickle'
    ]

    item_url_base = 'https://ebooks.lyrasistechnology.org/190150/book/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Fworks%2FURI%2Fhttp%3A%2F%2Flibrary.oapen.org%2Fhandle%2F20.500.12657%2F'

    the_output = [['COLL', 'ID', 'BIBID', 'HREF']]

    # Add rows for items within each collection
    for p in the_pickles:
        the_output += [
            [r['collection'],
             r['id'],
             r['bibid'],
             item_url_base + r['id']
             ]
            for r in get_bibs_and_ids(p)]

    out_sheet.clear()
    out_sheet.appendData(the_output)

    quit()


def get_bibs_and_ids(pickle_path):
    data = util.unpickle_it(pickle_path)['data']
    output = []
    for r in data:
        for e in r['metadata']:
            if e['key'] == 'dc.identifier.uri':
                the_uri = e['value']
                the_id = the_uri.split('/')[-1]
        output.append({'collection': r['cul_metadata']['collection_name'],
                       'bibid': r['cul_metadata']['bibid'],
                       'id': the_id})

    return output


def report_metadata(sheet_id, sheet_range, pickle_path):
    the_sheet = dataSheet(sheet_id, sheet_range)
    the_sheet.clear()
    the_bibs = [[r['bibid']] for r in get_bibs_and_ids(pickle_path)]
    # print(the_bibs)
    return the_sheet.appendData(the_bibs)


if __name__ == "__main__":
    main()
