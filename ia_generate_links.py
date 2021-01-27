# Script to output bibid and URLs for creating links from CLIO to SimplyE


import dcps_utils as util
import os
from sheetFeeder import dataSheet

my_path = os.path.dirname(__file__)


def main():
    # x = util.unpickle_it('output/ia/ia_ccny_feed.pickle')

    # from pprint import pprint
    # pprint(x)
    # quit()
    out_sheet = dataSheet(
        '1OG0UgqHCdAzx326JNy7akx9-MOwR9A_MSf-MEv9k3Ms', 'IA!A:Z')

    the_pickles = [
        'output/ia/ia_avt_feed.pickle',
        'output/ia/ia_ccny_feed.pickle',
        'output/ia/ia_durst_feed.pickle',
        'output/ia/ia_hebrewmss_feed.pickle',
        'output/ia/ia_med_feed.pickle',
        'output/ia/ia_mrp_feed.pickle',
        'output/ia/ia_mwm_feed.pickle',
        'output/ia/ia_wwi_feed.pickle'
    ]

    item_url_base = 'https://ebooks.lyrasistechnology.org/190150/book/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Fworks%2FURI%2Furn%3Ax-internet-archive%3Aebooks-app%3Aitem%3A'

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

    # Add CLC and LingLong
    the_output += [['Columbia Library Columns', 'ldpd_6309312_000', '6309312', 'https://ebooks.lyrasistechnology.org/190150/collection/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Ffeed%2F175%3Fentrypoint%3DBook'],
                   ['Ling Long', 'linglong_1931_000', '11500540', 'https://ebooks.lyrasistechnology.org/190150/collection/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Fgroups%2F176%3Fentrypoint%3DBook']]

    # print(the_output)

    out_sheet.clear()
    out_sheet.appendData(the_output)

    quit()


def get_bibs_and_ids(pickle_path):
    data = util.unpickle_it(pickle_path)
    return [{'collection': r['cul_metadata']['collection_name'],
             'bibid': r['cul_metadata']['bibid'],
             'id': r['identifier']} for r in data]


if __name__ == "__main__":
    main()
