from configparser import ConfigParser
import csv
import json
import os
import importlib.util
import sys


MY_PATH = os.path.dirname(__file__)

def pickle_utils():
    rel_path = os.path.join(MY_PATH, "..","..","dcps","pickle_utils.py")
    spec = importlib.util.spec_from_file_location("dcps.pickle_utils", rel_path)
    m = importlib.util.module_from_spec(spec)
    sys.modules["dcps.pickle_utils"] = m
    spec.loader.exec_module(m)
    return m

def main():
    config_path = os.path.join(MY_PATH, '..', '..', "config.ini")
    config = ConfigParser()
    config.read(config_path)
    csv_path = config['CSV']['springer_subjects']
    with open(csv_path, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        out_path = os.path.join(
            MY_PATH, '..', '..', 'output_test/springer/springer_subjects.pickle')
        subject_data = get_subjects(csv_reader)

        print(pickle_utils().pickle_it(subject_data, out_path))

    quit()


def get_subjects(csv_reader, head_row=True):
    """Retrieve list of dicts of format {'doi': <doi>, 'subjects': [<list of terms>]}
    Args:
        data_sheet (dataSheet): sheet containing Springer subject data.
        head_row (boolean): if True, ignore first row.
    """
    subject_data = {}
    if head_row:
        csv_reader.__next__()
    for row in csv_reader:
        doi = row[0]
        if doi == '10.1007/978-1-4899-6580-6': print("found 10.1007/978-1-4899-6580-6")
        subjects = [row[x + 1] for x in range(len(row) - 1)]
        subject_data[doi] = subjects

    return subject_data


if __name__ == "__main__":
    main()
