import json
import os
from sheetFeeder import dataSheet
from pprint import pprint
from dcps_utils import pickle_it


MY_PATH = os.path.dirname(__file__)


def main():
    the_sheet = dataSheet(
        '1D2E5Sm3qZdU3MGXk7q2XxfBpQS1iqauQm19f_y9aTbM', 'Sheet1!A:Z')

    out_path = os.path.join(
        MY_PATH, 'output_test/springer/springer_subjects.pickle')
    subject_data = get_subjects(the_sheet)

    print(pickle_it(subject_data, out_path))

    # pprint(subject_data)

    quit()


def get_subjects(data_sheet, head_row=True):
    """Retrieve list of dicts of format {'doi': <doi>, 'subjects': [<list of terms>]}
    Args:
        data_sheet (dataSheet): sheet containing Springer subject data.
        head_row (boolean): if True, ignore first row.
    """
    subject_data = {}
    the_data = data_sheet.getData()
    if head_row:
        the_data.pop(0)
    for r in the_data:
        doi = r[0]
        # primary_subject = r[1]
        subjects = [r[x + 1] for x in range(len(r) - 1)]
        subject_data[doi] = subjects

    return subject_data


if __name__ == "__main__":
    main()
