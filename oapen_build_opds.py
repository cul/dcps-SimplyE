# Script to compose OPDS feed from output of oapen_extract_data.

from lxml import etree
import dcps_utils as util
from datetime import datetime
from opds_validate import validate_files

# Set to True to output XML to output_test folder.
DEBUG = True

contentProvider = "OAPEN"

NSMAP = {None: "http://www.w3.org/2005/Atom",
         'app': "http://www.w3.org/2007/app",
         'bibframe': "http://bibframe.org/vocab/",
         'dcterms': "http://purl.org/dc/terms/",
         'simplified': "http://librarysimplified.org/terms/",
         'opds': "http://opds-spec.org/2010/catalog",
         'schema': "http://schema.org/",
         'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}


def main():

    x = build_feed('output/oapen/oapen_clio.pickle', 'books', chunk_size=100)

    # print(x)
    quit()


def make_entry(_parent, _dict, _bibid):
    ns_bibframe = "{%s}" % NSMAP["bibframe"]
    ns_dcterms = "{%s}" % NSMAP["dcterms"]
    ns_simplified = "{%s}" % NSMAP["simplified"]
    ns_rdf = "{%s}" % NSMAP["rdf"]

    # process bitstreams (binary file links)
    e_bitstreams = process_bitstreams(_dict['bitstreams'])
    e_metadata = _dict['metadata']

    if e_bitstreams and ('link_pdf' or 'link_epub') in e_bitstreams:
        # if there is no bitstream data, we can't use the entry.
        # TODO: test if either PDF or EPUB.

        # Create <entry> element
        entry = etree.SubElement(_parent, "entry")

        # Add elements within entry
        e_id = etree.SubElement(entry, "id")
        # e_id.text = e_metadata['id']
        e_id.text = metadata_finder(e_metadata, 'dc.identifier.uri')[0]

        # search for authors
        author_data = metadata_finder(e_metadata, 'dc.contributor.author')
        print(author_data)
        # e_metadata['authors'] = [{'a_name': a} for a in author_data]

        # for aut in e_metadata['authors']:
        for aut in author_data:
            e_author = etree.SubElement(entry, "author")
            e_author_name = etree.SubElement(e_author, "name")
            e_author_name.text = aut
            e_author_name_sort = etree.SubElement(
                e_author, ns_simplified + "sort_name")
            e_author_name_sort.text = aut

        e_title = etree.SubElement(entry, "title")
        print(_dict['name'])
        e_title.text = _dict['name']
        e_dist = etree.SubElement(
            entry, ns_bibframe + "distribution",  ProviderName=contentProvider)
        if 'link_pdf' in e_bitstreams:
            e_link_pdf = etree.SubElement(
                entry, "link", href=e_bitstreams['link_pdf'],
                type="application/pdf",
                rel="http://opds-spec.org/acquisition/open-access")
        if 'link_epub' in e_bitstreams:
            e_link_epub = etree.SubElement(
                entry, "link", href=e_bitstreams['link_epub'],
                type="application/epub+zip",
                rel="http://opds-spec.org/acquisition/open-access")
        if 'link_cover' in e_bitstreams:
            print(e_bitstreams['link_cover'])
            e_link_cover = etree.SubElement(
                entry, "link", href=e_bitstreams['link_cover'], type="image/jpeg", rel="http://opds-spec.org/image")
            e_link_cover = etree.SubElement(
                entry, "link", href=e_bitstreams['link_cover'], type="image/jpeg", rel="http://opds-spec.org/image/thumbnail")

        # e_summary = etree.SubElement(entry, "summary", type="text")
        # e_updated = etree.SubElement(entry, "updated")
        # e_issued = etree.SubElement(entry, ns_dcterms + "issued")
        # e_published = etree.SubElement(entry, "published")

        # pub dates
        pub_issued = metadata_finder(e_metadata, 'dc.date.issued')
        if pub_issued:
            e_issued = etree.SubElement(entry, ns_dcterms + "issued")
            e_issued.text = pub_issued[0]

        # Published should be same as issued? Not sure if .available is correct.
        pub_published = metadata_finder(e_metadata, 'dc.date.available')
        if pub_published:
            e_published = etree.SubElement(entry, "published")
            e_published.text = pub_published[0]

        # # updated
        e_updated = etree.SubElement(entry, "updated")
        # e_updated.text = convert_date(_dict['lastModified'])
        e_updated.text = now

        # updated = metadata_finder(e_metadata, "dc.date.available")
        # if updated:
        #     e_updated = etree.SubElement(entry, "updated")
        #     e_updated.text = updated[0]

        # Language
        languages = metadata_finder(
            e_metadata, 'dc.language', result_key='code')
        if languages:
            for l in languages:
                e_language = etree.SubElement(entry, ns_dcterms + "language")
                e_language.text = l

        # # Summary
        # summary = metadata_finder(e_metadata, 'dc.description.abstract')
        # if summary:
        #     e_summary = etree.SubElement(entry, "summary", type="text")
        #     e_summary.text = summary[0]

        # CLIO reference (Not used by SimplyE but to be more easily parsed for reporting etc.)
        e_catlink = etree.SubElement(entry, ns_dcterms + 'isReferencedBy')
        e_catlink.attrib[ns_rdf + 'resource'] = 'https://clio.columbia.edu/catalog/' + \
            str(_bibid)

        # Content
        content = metadata_finder(e_metadata, 'dc.description.abstract')
        e_content = etree.SubElement(entry, "content", type="text/html")
        if content:
            e_content_p1 = etree.SubElement(e_content, "p")
            e_content_p1.text = content[0]
        e_content_p2 = etree.SubElement(e_content, "p")
        e_content_clio_link = etree.SubElement(
            e_content_p2, "a", href='https://clio.columbia.edu/catalog/' + str(_bibid))
        e_content_clio_link.text = clio_string

        # publisher
        publisher = metadata_finder(e_metadata, 'publisher.name')
        if publisher:
            e_summary = etree.SubElement(entry, ns_dcterms + "publisher")
            e_summary.text = publisher[0]

        # Audience
        e_audience = etree.SubElement(
            entry, "category", term="Adult", label="Adult", scheme="http://schema.org/audience")

        # Nonfiction
        # TODO: check that this applies to all
        e_fiction_category = etree.SubElement(entry, "category", term="http://librarysimplified.org/terms/fiction/Nonfiction",
                                              label="Nonfiction", scheme="http://librarysimplified.org/terms/fiction/")

        # Subjects
        subjs = metadata_finder(e_metadata, 'dc.subject.other')
        if subjs:
            for s in subjs:
                e_subj = etree.SubElement(
                    entry, "category", term=s, label=s, scheme="http://www.bic.org.uk/7/BIC-Standard-Subject-Categories/")


def metadata_finder(_list, _keyValue, result_key='value'):
    return [m[result_key]
            for m in _list if result_key in m and m['key'] == _keyValue]


def process_bitstreams(_list):

    url = 'https://library.oapen.org'

    result = {}
    if len(_list) > 0:
        for b in _list:
            if b['mimeType'] == "application/pdf":
                result['link_pdf'] = url + b["retrieveLink"]
            elif b['mimeType'] == "application/epub+zip":
                result['link_epub'] = url + b["retrieveLink"]
            elif b['mimeType'] == "image/jpeg":
                result['link_cover'] = url + b["retrieveLink"]
            elif b['mimeType'] == "text/plain":
                result['link_text'] = url + b["retrieveLink"]

    return result


def convert_date(_datetime):
    # Convert date of format "2020-04-02 12:32:17.628" to ISO
    d = datetime.strptime(_datetime, '%Y-%m-%d %H:%M:%S.%f')
    return d.isoformat()


def divide_list(lst, n):
    # generate n-sized chunks from list.
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def build_feed(pickle_path, collection_abbr, chunk_size=100):
    # Saves output to XML file(s). Returns error data (missing elements, etc.)
    # to be sent to report datasheet.
    global clio_string
    clio_string = "Go to catalog record in CLIO."
    global now
    # now = datetime.today().isoformat()  # Current timestamp in ISO
    now = datetime.utcnow().strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ")  # Current timestamp in ISO
    base_url = "https://ebooks.library.columbia.edu/static-feeds/oapen/" + \
        collection_abbr + "/"
    if DEBUG is True:
        base_folder = 'output_test/oapen/' + collection_abbr + '/'
    else:
        base_folder = 'output/oapen/' + collection_abbr + '/'

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

    print("")
    print("Validating files in " + base_folder)

    val = validate_files(base_folder)

    errs = any(v['errors'] for v in val)
    if errs:
        print("Validation errors!")
        print(val)
    else:
        print("All XML files are valid.")

    return(report_data)


if __name__ == "__main__":
    main()
