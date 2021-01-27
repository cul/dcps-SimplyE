# Script to read data about assets and compose links to CM assets for addition as 856 fields.

import dcps_utils as util
from sheetFeeder import dataSheet
from pprint import pprint


def main():

    sheet_id = '1yTDyd5GQFEsVBiKOnt5T1ejBdXhxhmXVUn6jQ-dg_5I'
    # the_voyager_range = 'Durst!A:Z'
    the_voyager_range = 'MWM!A:Z'
    the_ingest_range = 'ingested!A:Z'
    the_output_range = 'test!A:Z'

    the_data = dataSheet(sheet_id, the_voyager_range).getData()
    the_ingested = [x[0] for x in dataSheet(
        sheet_id, the_ingest_range).getData()]  # list of IA ids that are in the IA collection.

    the_output_sheet = dataSheet(sheet_id, the_output_range)

    the_heads = ['bibid', 'id', 'label', 'url', 'composed', 'in collection?']
    the_new_data = [the_heads]

    for a_row in the_data:

        bibid = a_row[0]
        the_920 = a_row[4]
        if the_920:
            # print(parse_920(the_920))
            parsed = parse_920(the_920)

            for d in parsed:
                if 'archive.org' in d['url']:

                    # id = d['url'].split('/')[-1]
                    id = (d['url'][:-1] if d['url'].endswith('/')
                          else d['url']).split('/')[-1]
                    match_flag = "Y" if id in the_ingested else "N"
                    url = 'https://ebooksbeta.lyrasistechnology.org/columbia/book/URI%2Furn%3Ax-internet-archive%3Aebooks-app%3Aitem%3A' + id
                    if 'label' in d:
                        label = 'Read on mobile (' + d['label'] + ')'
                    else:
                        label = "Read on mobile"
                    composed = '$3' + label + '$u' + url
                    the_new_data.append(
                        [bibid, id, label, url, composed, match_flag])

    print(the_new_data)

    the_output_sheet.clear()

    post = the_output_sheet.appendData(the_new_data)
    print(post)


def parse_920(data):
    the_result = []
    # the_920_list = data.split(';')

    x = data.split(';$',)  # need to split on char combo to be sure
    the_920_list = []
    for i in x:  # regularize beginnings of strings to $3, $u, or $z
        if i[0] != '$':
            the_920_list.append('$' + i)
        else:
            the_920_list.append(i)

    for x in the_920_list:
        a_920 = {}
        decomposed_920 = x.split('$')
        decomposed_920.pop(0)
        if decomposed_920[0][0] == "3":
            a_920['label'] = decomposed_920[0][1:]
            a_920['url'] = decomposed_920[1][1:]
        else:
            a_920['url'] = decomposed_920[0][1:]

        the_result.append(a_920)

    return the_result


if __name__ == '__main__':
    main()
