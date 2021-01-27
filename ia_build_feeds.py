# Script to build OPDS feeds for a list of pickled collection files
# (output from ia_get_collections).

import ia_opds_functions as ia
from pprint import pprint
import dcps_utils as util
from sheetFeeder import dataSheet

the_out_sheet = dataSheet(
    '1yTDyd5GQFEsVBiKOnt5T1ejBdXhxhmXVUn6jQ-dg_5I', 'errors!A:Z')

# the_collections = [('output/ia/ia_avt_feed.pickle', 'avt'),
#                    ('output/ia/ia_ccny_feed.pickle', 'ccny'),
#                    ('output/ia/ia_durst_feed.pickle', 'durst'),
#                    ('output/ia/ia_med_feed.pickle', 'med'),
#                    ('output/ia/ia_mrp_feed.pickle', 'mrp'),
#                    ('output/ia/ia_mwm_feed.pickle', 'mwm'),
#                    ('output/ia/ia_wwi_feed.pickle', 'wwi'),
#                    ('output/ia/ia_clc_feed.pickle', 'clc'), 
#                    ]
the_collections = [('output/ia/ia_hebrewmss_feed.pickle', 'hebrewmss'),
                   ]

for col in the_collections:
    x = ia.build_feed(col[0], col[1])
    the_out_sheet.appendData(x)


quit()
