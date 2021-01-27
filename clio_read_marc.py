import dcps_utils as util
from sheetFeeder import dataSheet
from pymarc import MARCReader
# from pprint import pprint


def main():

    x = util.get_clio_marc('11256832')

    reader = MARCReader(x)
    for record in reader:
        print(record.title())


if __name__ == '__main__':
    main()
