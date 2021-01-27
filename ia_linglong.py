import ia_opds_functions as ia
from sheetFeeder import dataSheet
from pprint import pprint
import dcps_utils as util


sheet_id = '1yTDyd5GQFEsVBiKOnt5T1ejBdXhxhmXVUn6jQ-dg_5I'


def main():

    build_linglong_feed()

    quit()


def get_linglong():
    # Get the linglong data from IA and save in one pickle per year (vol).
    the_sheet = dataSheet(
        sheet_id, 'LingLong!A:Z')

    output_folder = 'output/ia/'

    the_input = the_sheet.getData()
    heads = the_input.pop(0)

    the_data = []

    for y in range(1931, 1938):
        the_data.append({'vol': y, 'items': [{'bibid': r[0], 'id': r[2], 'label': r[3]}
                                             for r in the_input if r[1] == str(y)]})

    pprint(the_data)

    for vol_data in the_data:
        print(' ')
        print(vol_data['vol'])
        feed_stem = 'ia_ll_' + str(vol_data['vol'])
        # print(vol_data['items'])
        the_extracts = ia.extract_data(
            vol_data['items'], feed_stem, 'Ling Long (' + str(vol_data['vol']) + ')')

        pprint(the_extracts['errors'])
        # pprint(the_extracts['data'][0]['description'])

        util.pickle_it(the_extracts['data'],
                       output_folder + feed_stem + '.pickle')


def build_linglong_feed():
    # Run after data has been extracted via get_linglong.
    the_out_sheet = dataSheet(
        sheet_id, 'errors!A:Z')

    for y in range(1931, 1938):
        x = ia.build_feed('output/ia/ia_ll_' + str(y) + '.pickle', 'll')
        the_out_sheet.appendData(x)


if __name__ == "__main__":
    main()
