# Functions to gather ids and bibids for AI assets linked
# from CLIO, harvest metadata from IA, and compose paginated
# OPDS feeds for use in SimplyE.

# internet archive python library docs:
# https://archive.org/services/docs/api/internetarchive/

# TODO: Add docstrings to fns

from internetarchive import get_item
from lxml import etree, html
# from lxml.builder import ElementMaker
import dcps_utils as util
from datetime import datetime
import re
import time


contentProvider = "CUL: Internet Archive"

# Namespaces to be used in feed.
NSMAP = {None: "http://www.w3.org/2005/Atom",
         'app': "http://www.w3.org/2007/app",
         'bibframe': "http://bibframe.org/vocab/",
         'dcterms': "http://purl.org/dc/terms/",
         'simplified': "http://librarysimplified.org/terms/",
         'opds': "http://opds-spec.org/2010/catalog",
         'schema': "http://schema.org/",
         'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}


def main():

    str = "Benchmark for Faithful Digital Reproductions of Monographs and Serials. Version 1. December 2002. 1 online resource. Forms part of: Carnegie Corporation of New York Records. Columbia University Catalog: go to CLIO"

    print(text_clean(str))

    # x = get_item('ldpd_14230789_000').files
    # from pprint import pprint
    # pprint(x)
    quit()
    x = util.unpickle_it('output/ia/ia_ccny_feed.pickle')

    # from pprint import pprint
    # pprint(x)
    for r in x:
        print(r['identifier'])
        print(r['cul_metadata']['bibid'])

    quit()


def extract_data(records, feed_stem, collection_title):
    # records is list of dicts of form:
    #     {'bibid': <bibid>, 'id':<ia_id>, 'label':<link_label>}
    # feed_stem is the label that will be used to name XML files, e.g.:
    #    'ia_mrp_feed'
    # collection_title is a human-readable string, e.g.:
    #    "Missionary Research Pamphlets"
    # Returns dict of format {'data': the_output, 'errors': the_errors}

    the_output = []
    the_errors = []

    # check for duplicate ids and report them (they will be processed anyway)
    the_ids = [r['id'] for r in records]
    dupe_ids = find_duplicates(the_ids)
    dupe_errors = [[str(datetime.today()), feed_stem, r['bibid'], r['id'], 'Duplicate ID']
                   for r in records if r['id'] in dupe_ids]
    # pprint(dupe_errors)
    the_errors += dupe_errors

    for record in records:
        # print(record['id'])
        # clio_status = util.check_clio_status(record['bibid'])
        # if clio_status != 200:
        #     print('HTTP status: ' + str(clio_status))
        #     # Bibid is not in CLIO; note problem and skip.
        #     print('ERROR: No CLIO record found for ' +
        #           record['bibid'] + ' : ' + record['id'] + ' ('
        #           + str(clio_status) + ')! Skipping...')
        #     the_errors.append(
        #         [str(datetime.today()), feed_stem, record['bibid'], record['id'], 'BIBID not in CLIO! (' + str(clio_status) + ')'])
        #     time.sleep(2)
        #     continue

        record_files = get_item(record['id']).files
        record_metadata = get_item(record['id']).metadata
        if not record_metadata:
            # There was no data from the API
            print('ERROR: No data for ' +
                  record['bibid'] + ' : ' + record['id'] + '! Skipping...')
            the_errors.append(
                [str(datetime.today()), feed_stem, record['bibid'], record['id'], 'No data!'])
            continue

        if all('.pdf' not in f['name'] for f in record_files):
            # There is data but no PDF derivative to use.
            print('ERROR: No PDF available for ' +
                  record['bibid'] + ' : ' + record['id'] + '! Skipping...')
            the_errors.append(
                [str(datetime.today()), feed_stem, record['bibid'], record['id'], 'No PDF file!'])
            continue

        # Add the metadata to the output
        print(record_metadata['identifier'] +
              ': ' + record_metadata['title'])
        # Add CUL-specific metadata for use in generating feed XML.
        record_metadata['cul_metadata'] = {'bibid': record['bibid'],
                                           'feed_id': feed_stem,
                                           'collection_name':
                                           collection_title,
                                           'label': record['label']}
        the_output.append(record_metadata)

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


def parse_920(_str):
    # Parse a string and extract the $3 subfield
    # as ['label'] and $u or $a as ['id']
    results = {}
    p = re.compile('\$3(.*?)(;|\$|$)')
    match_label = p.match(_str)
    results['label'] = match_label.group(1) if match_label else None
    p = re.compile('.*\$[ua]http.*?archive\.org/details/(.*?)(;|\$|$)')
    match_id = p.match(_str)
    results['id'] = match_id.group(1) if match_id else None
    return results


def build_feed(pickle_path, collection_abbr, chunk_size=100, output_dir='output/ia'):
    # Saves output to XML file(s). Returns error data (missing elements, etc.)
    # to be sent to report datasheet.
    global clio_string
    clio_string = "Go to catalog record in CLIO."
    global now
    # now = datetime.today().isoformat()  # Current timestamp in ISO
    now = datetime.utcnow().strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ")  # Current timestamp in ISO
    base_url = "https://ebooks.library.columbia.edu/static-feeds/ia/" + collection_abbr + "/"
    base_folder = output_dir + '/' + collection_abbr + '/'

    # Unpack the data
    the_records = util.unpickle_it(pickle_path)['data']

    # some collection-level info to use
    feed_stem = the_records[0]['cul_metadata']['feed_id']
    collection_title = the_records[0]['cul_metadata']['collection_name']

    # Divide list into chunks
    total_count = len(the_records)
    print('Total count: ' + str(total_count))
    running_count = 0
    the_chunks = divide_list(the_records, chunk_size)

    for idx, record_chunk in enumerate(the_chunks):

        report_data = []

        running_count += len(record_chunk)
        print('Running_count = ' + str(running_count))
        print('')
        page_no = idx + 1
        if page_no > 1:
            feed_name = feed_stem + '_p' + str(page_no) + '.xml'
        else:
            feed_name = feed_stem + '.xml'

        feed_next_name = feed_stem + '_p' + str(page_no + 1) + '.xml'

        # Set up root and top-level elements
        root = etree.Element("feed", nsmap=NSMAP)
        feed_id = etree.SubElement(root, "id")
        feed_id.text = base_url + feed_stem
        feed_title = etree.SubElement(root, "title")
        # feed_title.text = collection_title + " | Columbia University Libraries"
        feed_title.text = collection_title
        feed_updated = etree.SubElement(root, "updated")
        feed_updated.text = now

        feed_link = etree.SubElement(
            root, "link", href=base_url + feed_name, rel="self")

        # Add feed_next, only if it is not the last one
        if running_count < total_count:
            feed_link_next = etree.SubElement(
                root, "link", href=base_url + feed_next_name, rel="next", title="Next")

        for record in record_chunk:
            bibid = record['cul_metadata']['bibid']

            e = make_entry(root, record, bibid)
            if e:  # if there are errors emanating from entry, add them to dict.
                # pprint(e)
                error_report = [str(now), collection_title, feed_name,
                                bibid, record['identifier'], '; '.join(e)]
                report_data.append(error_report)

        # Save result xml tree
        with open(base_folder + feed_name, 'wb') as f:
            f.write(etree.tostring(root, pretty_print=True))

    return(report_data)

    # fin


def make_entry(_parent, _dict, _bibid):
    # Add an entry in XML tree to specified parent node.

    # collect errors to return for reporting
    global errors
    errors = []

    if not(_dict):
        # If IA returns no data
        print("No data! Skipping...")
        errors.append('Error: No data!')
        return errors

    # ia_base_url = 'https://archive.org/download/'
    ia_base_url = 'https://archive.org/'
    # define namespaces
    ns_bibframe = "{%s}" % NSMAP["bibframe"]
    ns_dcterms = "{%s}" % NSMAP["dcterms"]
    ns_rdf = "{%s}" % NSMAP["rdf"]
    ns_simplified = "{%s}" % NSMAP["simplified"]

    # Create <entry> element
    entry = etree.SubElement(_parent, "entry")

    # Add subelements using functions
    add_subelement(entry, "id", "identifier", _dict,
                   formated="urn:x-internet-archive:ebooks-app:item:%s")
    add_subelement(entry, "title", "title", _dict)
    add_subelement_static(entry, "distribution",
                          nspace=ns_bibframe, ProviderName=contentProvider)

    # Authors/creators
    if 'creator' in _dict:
        the_creators = _dict['creator']
        if type(the_creators) == list:
            for c in the_creators:
                e_author = etree.SubElement(entry, "author")
                add_subelement_static(e_author, "name", c)
                add_subelement_static(e_author, "sort_name",
                                      c, nspace=ns_simplified)
        else:
            c = the_creators
            e_author = etree.SubElement(entry, "author")
            add_subelement_static(e_author, "name", c)
            add_subelement_static(e_author, "sort_name",
                                  c, nspace=ns_simplified)
    else:
        print('Warning: No *creator* key value!')
        errors.append('creator')

    # Links to resources
    add_subelement_static(entry, "link", href=ia_base_url + "cors/" + str(_dict['identifier']) + "/" + str(
        _dict['identifier']) + ".pdf", type="application/pdf", rel="http://opds-spec.org/acquisition/open-access")
    add_subelement_static(entry, "link", href=ia_base_url + "download/" + str(
        _dict['identifier']) + "/page/cover_medium.jpg", type="image/jpeg", rel="http://opds-spec.org/image")
    add_subelement_static(entry, "link", href=ia_base_url + "download/" + str(
        _dict['identifier']) + "/page/cover_medium.jpg", type="image/jpeg", rel="http://opds-spec.org/image/thumbnail")

    # === OPDS spec on dates ===
    # OPDS Catalog Entries must include an atom:updated element indicating when the OPDS Catalog Entry was last updated. A dc:issued element should be used to indicate the first publication date of the Publication and must not represent any date related to the OPDS Catalog Entry.

    # issued date
    add_subelement(entry, "issued", "date", _dict, nspace=ns_dcterms)

    # published date
    add_subelement_static(entry, "published",
                          convert_date(_dict["publicdate"]))

    # publisher
    add_subelement(entry, "publisher", "publisher", _dict, nspace=ns_dcterms)

    # updated
    add_subelement_static(entry, "updated", now)

    # language (Note, language is required)
    add_subelement(entry, "language", "language", _dict, nspace=ns_dcterms)

    # Add catalog link
    # TODO: need to add rdf: to attribute
    # add_subelement_static(entry, "isReferencedBy",
    #                       nspace=ns_dcterms, ns_rdf + resource='https://clio.columbia.edu/catalog/' + str(_bibid))
    e_catlink = etree.SubElement(entry, ns_dcterms + 'isReferencedBy')
    e_catlink.attrib[ns_rdf + 'resource'] = 'https://clio.columbia.edu/catalog/' + \
        str(_bibid)
    # etree.s (entry, "isReferencedBy",
    #                       nspace=ns_dcterms, ns_rdf + resource='https://clio.columbia.edu/catalog/' + str(_bibid))

    # e_elem = etree.SubElement(_parent, nspace + _element_name, kwargs)
    # add_subelement(entry, "isReferencedBy", "language", _dict, nspace=ns_dcterms)
    #     <dcterms:isReferencedBy rdf:resource="https://clio.columbia.edu/catalog/13085586"/>

    # Content block
    e_content = etree.SubElement(entry, "content", type="text/html")
    if 'description' in _dict:
        if type(_dict['description']) == str:
            e_content.append(fragment_cleaner(
                text_clean(_dict['description'])))
        else:
            desc = text_clean(('. ').join(_dict['description']))
            e_content.append(fragment_cleaner(desc))
    else:
        print('Warning: No description.')
        errors.append('description')
    e_content_p2 = etree.SubElement(e_content, "p")
    e_content_clio_link = etree.SubElement(
        e_content_p2, "a", href='https://clio.columbia.edu/catalog/' + str(_bibid))
    e_content_clio_link.text = clio_string

    # Generic classifcation
    # Audience
    add_subelement_static(entry, "category", term="Adult",
                          label="Adult", scheme="http://schema.org/audience")

    # Nonfiction
    # TODO: check that this applies to all
    add_subelement_static(entry, "category", term="http://librarysimplified.org/terms/fiction/Nonfiction",
                          label="Nonfiction", scheme="http://librarysimplified.org/terms/fiction/")

    # Subjects
    if 'subject' in _dict:
        the_subjects = _dict['subject']
        if type(the_subjects) == str:
            # string, not a list
            add_subelement_static(
                entry, "category", term=the_subjects, label=the_subjects)
        else:
            for s in the_subjects:
                add_subelement_static(entry, "category", term=s, label=s)
    else:
        print('Warning: No subjects.')
        errors.append('subject')

    # End entry and return list of errors/warnings to parent
    return errors


def add_subelement(_parent, _element_name, _source_key, _dict, formated='%s', nspace='', **kwargs):
    # append an element to a parent drawing from given key in given dict. Kwargs are added as attributes.
    if _source_key in _dict:
        if type(_source_key) == list:
            print("Warning: " + _source_key + " has more than one value!")
            errors.append(_source_key)
        else:
            e_elem = etree.SubElement(_parent, nspace + _element_name, kwargs)
            e_elem.text = formated % _dict[_source_key]
    else:
        print('Warning: no *' + _source_key + '* key value!')
        errors.append(_source_key)


def add_subelement_static(_parent, _element_name, _text="", nspace='', **kwargs):
    # append an element to a parent with given text and attributes (kwargs). If no text then creates empty element.
    e_elem = etree.SubElement(_parent, nspace + _element_name, kwargs)
    if _text:
        e_elem.text = _text


def fragment_cleaner(_str):
    """Remove extraneous markup from description text, leaving only <p> container.

    Args:
        _str (String): String containing markup

    Returns:
        [String]: Cleaned up text.
    """
    x = html.fragment_fromstring(_str, create_parent='p')
    etree.strip_tags(x, '*')
    return x


def convert_date(_datetime):
    # Convert date of format "2020-04-02 12:32:17.628" to ISO
    # d = datetime.strptime(_datetime, '%Y-%m-%d %H:%M:%S.%f')
    d = datetime.strptime(_datetime, '%Y-%m-%d %H:%M:%S')
    return d.isoformat()


def divide_list(lst, n):
    """Generate n-sized chunks from list

    Args:
        lst (list): A list
        n (int): chunk size

    Yields:
        generator: set of n-size lists
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def text_clean(the_str):
    # Remove the useless "Go to CLIO" non-links from descriptions.
    the_str = re.sub(
        '(<b>)?Columbia University Catalog: (</b>)?(<a.*?>)?go to CLIO(</a>)?', '', the_str)
    return the_str


if __name__ == "__main__":
    main()
