# Script to harvest oapen data and transform to OPDS.
# TODO: everything!

import requests
import json
from pprint import pprint
import dcps_utils as util


the_collections = [
    {"name": "ERC", "url": "http://library.oapen.org/rest/search?query=oapen.collection:%22European%20Research%20Council%22&expand=metadata,bitstreams&limit=1000"}]

for c in the_collections:
    collection_data = json.loads(requests.get(c["url"]).text)

    util.pickle_it(collection_data, 'output/' +
                   "oapen_" + c["name"] + "_data.pickle")
