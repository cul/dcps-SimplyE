# Script to build OPDS feeds for a list of pickled collection files
# (output from ia_get_collections).

import ia_opds_functions as ia
from pprint import pprint
import dcps_utils as util
from sheetFeeder import dataSheet
from ia_linglong import build_linglong_feed
import opds_validate


TEST = True

OUTPUT_DIR = 'output_test/ia' if TEST else 'output/ia'
# SHEET_ID = '1yTDyd5GQFEsVBiKOnt5T1ejBdXhxhmXVUn6jQ-dg_5I'
SHEET_ID = '1sQBo05FvQ8Z6Yi-shBWRHYdgDgjQPdD2SgP-6-NigGg'


def main():
    """Script to compose OPDS v1.2 XML feeds using data saved from ia_get_collections.py.
    Modify list of collections as needed.
    """
    the_out_sheet = dataSheet(
        SHEET_ID, 'errors!A:Z')

    the_collections = [
        (OUTPUT_DIR + '/ia_avt_feed.pickle', 'avt'),
        (OUTPUT_DIR + '/ia_ccny_feed.pickle', 'ccny'),
        (OUTPUT_DIR + '/ia_durst_feed.pickle', 'durst'),
        (OUTPUT_DIR + '/ia_med_feed.pickle', 'med'),
        (OUTPUT_DIR + '/ia_mrp_feed.pickle', 'mrp'),
        (OUTPUT_DIR + '/ia_mwm_feed.pickle', 'mwm'),
        (OUTPUT_DIR + '/ia_wwi_feed.pickle', 'wwi'),
        # ('output/ia/ia_clc_feed.pickle', 'clc'),
        (OUTPUT_DIR + '/ia_hebrewmss_feed.pickle', 'hebrewmss'),
        # ('output/ia/ia_tibetan_feed.pickle', 'tibet'),
    ]

    for col in the_collections:
        x = ia.build_feed(col[0], col[1], output_dir=OUTPUT_DIR)
        the_out_sheet.appendData(x)

    # build_linglong_feed(output_dir=OUTPUT_DIR)

    # validate the output
    x = opds_validate.validate_files(OUTPUT_DIR)
    print(
        '\n'.join(
            '***ERROR!*** File ' + r['file'] + ' has errors: ' + r['errors']
            for r in x
            if r['errors']
        )
    )

    quit()


if __name__ == "__main__":
    main()
