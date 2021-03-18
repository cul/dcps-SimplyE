# Validate all the OPDS files in a given directory using the OPDS Relax Schema.

import dcps_utils as util
import os

my_path = os.path.dirname(__file__)

jing_path = os.path.join(
    my_path, '../resources/jing-20091111/bin/jing.jar')
schema_path = os.path.join(
    my_path, 'schemas/opds.rnc')


def main():

    output_base_dir = 'output_test/ia'
    # output_base_dir = 'output/ia'

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

        the_path = os.path.join(my_path, output_base_dir, c)
        val = validate_files(the_path)
        # print(val)
        the_errors = [f for f in val if f['errors']]
        if the_errors:
            print(the_errors)
        else:
            print('No validation errors in ' + c +
                  ' (' + str(len(val)) + ' files).')

    quit()


def validate_files(_dir):
    # Return a list of dicts of format
    # {'file':<filepath>,'errors':<error_output>}
    # No errors means file is valid.
    the_files = os.walk(_dir)

    # Collect all the XML files into a list to validate.
    the_paths = []
    for root, dirs, files in the_files:
        the_paths += [os.path.join(root, name)
                      for name in files if '.xml' in name]

    the_output = []
    for a_file in the_paths:
        # print('Validating ' + a_file + ' ... ')
        errors = util.jing_process(jing_path,
                                   a_file, schema_path, compact=True)
        the_output.append({'file': a_file, 'errors': errors})
        # if errors:
        #     print('ERROR! ' + a_file + ': ' + errors)
    return the_output


if __name__ == "__main__":
    main()
