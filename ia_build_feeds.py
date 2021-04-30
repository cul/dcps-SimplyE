# Script to build OPDS feeds for a list of pickled collection files
# (output from ia_get_collections).

import ia_opds_functions as ia
from pprint import pprint
import dcps_utils as util
from sheetFeeder import dataSheet
from ia_linglong import build_linglong_feed
import opds_validate


TEST = True

output_dir = 'output_test/ia' if TEST else 'output/ia'

# x = util.unpickle_it('output/ia/ia_mwm_feed.pickle')
# pprint(x['data'][0])
# quit()

the_out_sheet = dataSheet(
    '1yTDyd5GQFEsVBiKOnt5T1ejBdXhxhmXVUn6jQ-dg_5I', 'errors!A:Z')

the_collections = [
    ('output/ia/ia_avt_feed.pickle', 'avt'),
    ('output/ia/ia_ccny_feed.pickle', 'ccny'),
    ('output/ia/ia_durst_feed.pickle', 'durst'),
    ('output/ia/ia_med_feed.pickle', 'med'),
    ('output/ia/ia_mrp_feed.pickle', 'mrp'),
    ('output/ia/ia_mwm_feed.pickle', 'mwm'),
    ('output/ia/ia_wwi_feed.pickle', 'wwi'),
    ('output/ia/ia_clc_feed.pickle', 'clc'),
    ('output/ia/ia_hebrewmss_feed.pickle', 'hebrewmss'),
    # ('output/ia/ia_tibetan_feed.pickle', 'tibet'),
]


for col in the_collections:
    x = ia.build_feed(col[0], col[1], output_dir=output_dir)
    the_out_sheet.appendData(x)

build_linglong_feed(output_dir=output_dir)


# validate the output
x = opds_validate.validate_files(output_dir)
print(
    '\n'.join(
        '***ERROR!*** File ' + r['file'] + ' has errors: ' + r['errors']
        for r in x
        if r['errors']
    )
)


quit()
