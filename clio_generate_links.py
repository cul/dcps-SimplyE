# Script to output bibid and URLs for creating links from CLIO to SimplyE.
# Data sources are pickled data (IA, OAPEN) plus ONIX (JHUP and other TK)


import dcps_utils as util
import os
from sheetFeeder import dataSheet
import csv


my_path = os.path.dirname(__file__)


def main():

    # a = [['x', 'a', 1, 11], ['x', 'b', 2, 22], ['x', 'c', 3, 33], ]

    # print(trim_array(a, [1, 3]))
    # print(a)
    # quit()

    # print(util.unpickle_it('output/ia/ia_avt_feed.pickle')['data'][1]['title'])
    # quit()

    out_path = os.path.join(
        my_path, 'output/clio_links/simplye_clio_links.csv')

    # out_sheet = dataSheet(
    #     '1r8oaOQT955HvAii-5sF3IDwXR1_SGXx_KZRLN40JK9s', 'Sheet1!A:Z')
    out_sheet = dataSheet(
        '1r8oaOQT955HvAii-5sF3IDwXR1_SGXx_KZRLN40JK9s', 'Test!A:Z')  # Test

    csv_output = [['BIBID', 'HREF']]
    sheet_output = [['BIBID', 'VENDOR', 'COLLECTION', 'TITLE', 'ID', 'HREF']]

    print('*** Getting IA... ***')
    the_ia = get_ia()
    sheet_output += the_ia
    the_ia_extras = get_ia_serials()
    sheet_output += the_ia_extras
    print('*** ' + str(len(the_ia) + len(the_ia_extras)) + ' records added. ***')
    csv_output += util.trim_array(the_ia, [1, 2, 3, 4])
    csv_output += get_ia_serials_lookups()  # add in LingLong and CLC lookup

    print('*** Getting OAPEN... ***')
    the_oapen = get_oapen()
    print('*** ' + str(len(the_oapen)) + ' records added. ***')
    sheet_output += the_oapen
    csv_output += util.trim_array(the_oapen, [1, 2, 3, 4])

    # jhup_onix_path = '/Users/dwh2128/Documents/SimplyE/books/JHU/ONIX/ONIX3_converted/TO-IMPORT/v3/'
    jhup_onix_path = '/Users/dwh2128/Documents/SimplyE/books/JHU/ONIX/ONIX3_converted/TO-IMPORT/v4/out3'
    print('*** Getting JHUP... ***')
    the_jhup = get_onix(jhup_onix_path, 'Johns Hopkins University Press')
    # print(the_jhup)
    print('*** ' + str(len(the_jhup)) + ' records added. ***')
    sheet_output += the_jhup
    csv_output += util.trim_array(the_jhup, [1, 2, 3, 4])

    print('Total: ' + str(len(csv_output) - 1))

    out_sheet.clear()
    out_sheet.appendData(sheet_output)

    with open(out_path, mode='w') as f:
        w = csv.writer(f, delimiter=',', quotechar='"',
                       quoting=csv.QUOTE_MINIMAL)
        w.writerows(csv_output)

    quit()


def get_oapen():
    oapen_pickle = os.path.join(my_path, 'output/oapen/oapen_clio.pickle')

    oapen_prefix = 'http://library.oapen.org/handle/20.500.12657/'
    oapen_item_url_base = 'https://academic.lyrasistechnology.org/columbia/book/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Fworks%2FURI%2Fhttp%3A%2F%2Flibrary.oapen.org%2Fhandle%2F20.500.12657%2F'

    return [
        [
            r['bibid'],
            r['vendor'],
            r['collection'],
            r['title'],
            oapen_prefix + r['id'],
            oapen_item_url_base + r['id']
        ]
        for r in oapen_pickle_parse(oapen_pickle)]


def get_ia():

    ia_pickles = [
        'output/ia/ia_avt_feed.pickle',
        'output/ia/ia_ccny_feed.pickle',
        'output/ia/ia_durst_feed.pickle',
        'output/ia/ia_hebrewmss_feed.pickle',
        'output/ia/ia_med_feed.pickle',
        'output/ia/ia_mrp_feed.pickle',
        'output/ia/ia_mwm_feed.pickle',
        'output/ia/ia_wwi_feed.pickle',
        # 'output/ia/ia_ll_1931.pickle',
        # 'output/ia/ia_ll_1932.pickle',
        # 'output/ia/ia_ll_1933.pickle',
        # 'output/ia/ia_ll_1934.pickle',
        # 'output/ia/ia_ll_1935.pickle',
        # 'output/ia/ia_ll_1936.pickle',
        # 'output/ia/ia_ll_1937.pickle',
        # 'output/ia/ia_clc_feed.pickle',
    ]

    ia_prefix = 'urn:x-internet-archive:ebooks-app:item:'

    ia_item_url_base = 'https://academic.lyrasistechnology.org/columbia/book/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Fworks%2FURI%2Furn%3Ax-internet-archive%3Aebooks-app%3Aitem%3A'
    result = []
    for p in ia_pickles:
        result += [
            [
                r['bibid'],
                r['vendor'],
                r['collection'],
                r['title'],
                ia_prefix + r['id'],
                ia_item_url_base + r['id']
            ]
            for r in ia_pickle_parse(p)]

    return result


def get_ia_serials_lookups():
    # Add LingLong and CLC group URLs (not items)
    return [['6309312',
             'https://academic.lyrasistechnology.org/columbia/collection/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Ffeed%2F175%3Fentrypoint%3DBook'],
            ['11500540',
                'https://academic.lyrasistechnology.org/columbia/collection/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Fgroups%2F176%3Fentrypoint%3DBook']]


def get_ia_serials():
    # have to treat these separately as we are not adding
    # CLIO links at the item level. One link per serial.
    # This data only goes into the inventory sheet.

    ia_pickles = [
        'output/ia/ia_ll_1931.pickle',
        'output/ia/ia_ll_1932.pickle',
        'output/ia/ia_ll_1933.pickle',
        'output/ia/ia_ll_1934.pickle',
        'output/ia/ia_ll_1935.pickle',
        'output/ia/ia_ll_1936.pickle',
        'output/ia/ia_ll_1937.pickle',
        'output/ia/ia_clc_feed.pickle',
    ]

    ia_prefix = 'urn:x-internet-archive:ebooks-app:item:'

    ia_item_url_base = 'https://academic.lyrasistechnology.org/columbia/book/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Fworks%2FURI%2Furn%3Ax-internet-archive%3Aebooks-app%3Aitem%3A'
    result = []
    for p in ia_pickles:
        result += [
            [
                r['bibid'],
                r['vendor'],
                r['collection'],
                r['title'],
                ia_prefix + r['id'],
                ia_item_url_base + r['id']
            ]
            for r in ia_pickle_parse(p)]

    return result


def get_onix(input_dir, publisher):
    csv_path = os.path.join(
        my_path, 'output/clio_links/onix_clio_links.csv')  # temporary file
    xslt_path = os.path.join(
        my_path, 'xslt/onix_clio_csv.xsl')
    saxon_path = os.path.join(
        my_path, '../resources/saxon-9.8.0.12-he.jar')
    params = "input_dir=" + input_dir + " publisher='" + publisher + "'"
    print(params)
    util.saxon_process2(saxon_path, xslt_path, xslt_path, csv_path,
                        theParams=params)

    with open(csv_path, newline='') as f:
        reader = csv.reader(f, delimiter='|')
        # remove duplicates where there are both pdf and epub (same url)
        the_data = util.dedupe_array([row for row in reader], 0)
    the_data.pop(0)  # w/o heads
    return the_data


def ia_pickle_parse(pickle_path, vendor="Internet Archive"):
    data = util.unpickle_it(pickle_path)['data']
    return [{'vendor': vendor,
             'collection': r['cul_metadata']['collection_name'],
             'bibid': r['cul_metadata']['bibid'],
             'id': r['identifier'],
             'title':r['title']} for r in data]


def oapen_pickle_parse(pickle_path, vendor="OAPEN"):
    data = util.unpickle_it(pickle_path)['data']
    output = []
    for r in data:
        for e in r['metadata']:
            if e['key'] == 'dc.identifier.uri':
                the_uri = e['value']
                the_id = the_uri.split('/')[-1]
        output.append({
            'vendor': vendor, 'collection': r['cul_metadata']['collection_name'],
            'bibid': r['cul_metadata']['bibid'],
            'id': the_id, 'title': r['name']})
    return output


if __name__ == "__main__":
    main()
