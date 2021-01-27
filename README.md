# SimplyE Resources

These scripts are in development for the CUL SimplyE Ebook delivery project. See [SimplyE Ebook project wiki](https://wiki.library.columbia.edu/display/SET/SimplyE+E-book+Project).

## Internet Archive Scripts

### ia_get_collections.py

Extract data from a Google Sheet and use IDs to query IA API to retrieve metadata including acquisition links. The result is a pickled data file for each collection processed. The process merges BIBIDs along with other CUL-specific metadata with the data from the API, using an appended 'cul_metadata' object.

### ia_build_feeds.py

Transform pickled data from an IA collection into a paginated OPDS feed. Feeds are chunked into 100 entry pages. 

### ia_columbia_columns.py

Generates OPDS for the "Columbia Library Columns" periodical, using different input format.

### ia_linglong.py

Generates OPDS for the serial "Ling Long" periodical, using different input format.

### ia_opds_functions.py

Utility functions used by the other IA scripts.

## OAPEN Scripts

### oapen_extract_data.py

Extract data from OAPEN API, similar to ia_get_collections above. There is only one OAPEN collection.

### oapen_build_opds.py

Build paginated OPDS XML feed for OAPEN collection comparable to ia_build_feeds above. 

## General utilites

### opds_validate.py

Validate all OPDS files within a given path against schema.

### dcps_utils.py

General utilities imported and used across scripts.

### sheetFeeder.py

Abstraction of Google Sheets API, for reading and writing data to/from sheets. [See here for documentation.](https://github.com/dwhodges2/sheetFeeder)

