import ia_opds_functions as ia
from sheetFeeder import dataSheet
from pprint import pprint
import dcps_utils as util


SHEET_ID = '1yTDyd5GQFEsVBiKOnt5T1ejBdXhxhmXVUn6jQ-dg_5I'

OUTPUT_FOLDER = 'output/ia'


def main():
    """Script to compose OPDS feeds for Ling Long serials, one feed per volume for 1931–1938.
    """

    build_linglong_feed()

    quit()


def get_linglong():
    """Get the linglong data from IA and save in one pickle per year (vol).
    """
    the_sheet = dataSheet(
        SHEET_ID, 'LingLong!A:Z')

    the_input = the_sheet.getData()
    heads = the_input.pop(0)

    the_data = []

    for y in range(1931, 1938):
        the_data.append({'vol': y, 'items': [{'bibid': r[0], 'id': r[2], 'label': r[3]}
                                             for r in the_input if r[1] == str(y)]})

    # pprint(the_data)

    for vol_data in the_data:
        print(' ')
        print(vol_data['vol'])
        feed_stem = 'ia_ll_' + str(vol_data['vol'])
        pickle_path = OUTPUT_FOLDER + '/' + feed_stem + '.pickle'
        # print(vol_data['items'])
        feed_data = ia.extract_data(
            vol_data['items'], feed_stem, 'Ling Long (' + str(vol_data['vol']) + ')')

        pprint(feed_data['errors'])

        print('Saving ' + str(len(feed_data['data'])
                              ) + ' records to ' + pickle_path)

        util.pickle_it(feed_data, pickle_path)


def build_linglong_feed(pickle_dir=OUTPUT_FOLDER, output_dir=OUTPUT_FOLDER):
    """Run after data has been extracted via get_linglong.

    Args:
        pickle_dir (str, optional): Path to folder containing pickles. Defaults to OUTPUT_FOLDER.
        output_dir (str, optional): Path to output folder. Defaults to OUTPUT_FOLDER.
    """
    the_out_sheet = dataSheet(
        SHEET_ID, 'errors!A:Z')

    for y in range(1931, 1938):
        x = ia.build_feed(pickle_dir + '/ia_ll_' + str(y) +
                          '.pickle', 'll', output_dir=output_dir)
        the_out_sheet.appendData(x)


if __name__ == "__main__":
    main()
