# Validate all the OPDS files in a given directory using the OPDS Relax Schema.

import dcps_utils as util
import os

MY_PATH = os.path.dirname(__file__)

SCHEMA_PATH = os.path.join(MY_PATH, 'schemas/opds.rnc')


def main():
    """Validate all the OPDS files in a given directory using the OPDS Relax Schema.
    """
    # output_base_dir = 'output_test/ia'
    output_base_dir = 'output/ia'

    x = validate_files(output_base_dir)

    print(
        '\n'.join(
            'ERROR! File ' + r['file'] + ' has errors: ' + r['errors']
            for r in x
            if r['errors']
        )
    )
    quit()

    the_collections = ['avt',
                       'ccny',
                       'clc',
                       'durst',
                       'hebrewmss',
                       'll',
                       'med',
                       'mrp',
                       'mwm',
                       'wwi',
                       ]

    for c in the_collections:

        the_path = os.path.join(MY_PATH, output_base_dir, c)
        val = validate_files(the_path)
        # print(val)
        the_errors = [f for f in val if f['errors']]
        if the_errors:
            print(the_errors)
        else:
            print('No validation errors in ' + c +
                  ' (' + str(len(val)) + ' files).')

    quit()


def validate_files(_dir, schema_path=SCHEMA_PATH):
    """Validate OPDS v1.2 against schema.
    Return a list of dicts of errors matched to files.
    No errors means file is valid.

    Args:
        _dir (str): Path to folder of OPDS XML files
        schema_path (str, optional): Path to schema. Defaults to SCHEMA_PATH.

    Returns:
        list: [{'file':<filepath1>,'errors':<error_output1>}, 
        {'file':<filepath2>,'errors':<error_output2>} ...]
    """

    the_files = os.walk(_dir)

    # Collect all the XML files into a list to validate.
    the_paths = []
    for root, dirs, files in the_files:
        the_paths += [os.path.join(root, name)
                      for name in files if '.xml' in name]

    the_output = []
    for a_file in the_paths:
        # print('Validating ' + a_file + ' ... ')
        errors = util.jing_process(a_file, SCHEMA_PATH, compact=True)
        the_output.append({'file': a_file, 'errors': errors})
        # if errors:
        #     print('ERROR! ' + a_file + ': ' + errors)
    return the_output


if __name__ == "__main__":
    main()
