import subprocess
from configparser import ConfigParser
import os
import pickle
import requests
import copy
from io import StringIO
import csv


my_path = os.path.dirname(__file__)
# harvester_path = os.path.join(my_path, "pyoaiharvester/pyoaiharvest.py")
config_path = os.path.join(my_path, "config.ini")
config = ConfigParser()
config.read(config_path)


def oai_harvest(
    out_path,
    output_type="oai_marc",
    server="Prod",
    date_params="",
    harvester_path=os.path.join(my_path, "pyoaiharvester/pyoaiharvest.py"),
):

    if server == "Dev":
        oaiURL = config["DEV"]["baseOAIURL"]
    elif server == "Test":
        oaiURL = config["TEST"]["baseOAIURL"]
    else:
        oaiURL = config["PROD"]["baseOAIURL"]

    cmd = (
        "python "
        + harvester_path
        + " -l "
        + oaiURL
        + " -m "
        + output_type
        + " -s collection"
        + " -o "
        + out_path
        + " "
        + date_params
    )
    print(cmd)
    p = subprocess.Popen(
        [cmd],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    result = p.communicate()
    if result[1]:  # error
        return "PYOAIHARVEST ERROR: " + str(result[1].decode("utf-8"))
    else:
        return result[0].decode("utf-8")


def saxon_process(inFile, transformFile, outFile, theParams=" ", saxonPath=config['FILES']['saxonPath']):
    # Process an XSLT transformation. Use None for outFile to send to stdout.
    outStr = " > " + outFile if outFile else " "
    cmd = (
        "java -jar "
        + saxonPath
        + " "
        + inFile
        + " "
        + transformFile
        + " "
        + theParams
        + " "
        + "--suppressXsltNamespaceCheck:on"
        + outStr
    )
    # print(cmd)
    p = subprocess.Popen(
        [cmd],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    result = p.communicate()
    if result[1]:
        if "error" in str(result[1].decode("utf-8")).lower():
            # error
            raise Exception("SAXON ERROR: " + str(result[1].decode("utf-8")))
        elif "does not exist" in str(result[1].decode("utf-8")).lower():
            # error
            raise Exception("SAXON ERROR: " + str(result[1].decode("utf-8")))
        elif "java.io" in str(result[1].decode("utf-8")).lower():
            # error
            raise Exception("SAXON ERROR: " + str(result[1].decode("utf-8")))
        elif "permission denied" in str(result[1].decode("utf-8")).lower():
            # error
            raise Exception("SAXON ERROR: " + str(result[1].decode("utf-8")))
        else:
            # non-error output
            return "SAXON MESSAGE: " + str(result[1].decode("utf-8"))
    else:
        return result[0].decode("utf-8")


def jing_process(filePath, schemaPath, compact=False, jingPath=config['FILES']['jingPath']):
    # Process an xml file against a schema (rng or schematron) using Jing.
    # Tested with jing-20091111.
    # https://code.google.com/archive/p/jing-trang/downloads
    # -d flag (undocumented!) = include diagnostics in output.
    # -c flag is for compact schema format.
    flags = ' -cd ' if compact is True else ' -d '
    cmd = "java -jar " + jingPath + flags + schemaPath + " " + filePath
    # print(cmd)
    p = subprocess.Popen(
        [cmd],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    result = p.communicate()
    if result[1]:  # error
        return "SAXON ERROR: " + str(result[1].decode("utf-8"))
    else:
        return result[0].decode("utf-8")


def xml_to_array(in_file, xslt_file, delim='|', params=" "):
    # Process XML via XSLT to tabular format,
    # and then return as a list of lists.
    # Requires XSLT that outputs delimited plain text.
    tabular = saxon_process(in_file, xslt_file, None, theParams=params)
    f = StringIO(tabular)
    return list(csv.reader(f, delimiter=delim))


def rsync_process(fromPath, toPath, options, keyPath=config["FILES"]["keyPath"]):
    if keyPath:
        cmd = (
            '/usr/bin/rsync -zarvhe "ssh -i '
            + keyPath
            + '" '
            + options
            + " "
            + fromPath
            + " "
            + toPath
        )
    else:
        cmd = "/usr/bin/rsync -zavh " + options + " " + fromPath + " " + toPath

    print("Running command: " + cmd + " ...")
    print(" ")

    result = subprocess.Popen(
        [cmd],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    ).communicate()

    if result[1]:  # error
        return "RSYNC ERROR: " + str(result[1].decode("utf-8"))
    else:
        return result[0].decode("utf-8")


def pickle_it(obj, path):
    print("Saving pickle to " + str(path) + "...")
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def unpickle_it(path):
    print("Unpickling from " + str(path) + "...")
    with open(path, "rb") as f:
        output = pickle.load(f)
    return output


def get_clio_marc(bibid):
    url = 'https://clio.columbia.edu/catalog/' + str(bibid) + '.marc'
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as err:
        print('*** get_clio_marc request error: ' + str(err))
    else:
        # If the response was successful, no exception will be raised
        return response.content


def get_status(url):
    response = requests.get(url)
    return response.status_code


def check_clio_status(bibid):
    # If using in bulk, add sleep of .5 sec or more to
    # avoid "too many requests" error
    return get_status('https://clio.columbia.edu/catalog/' + str(bibid))


def diff(first, second):
    # Return list of x - y (everything in x that is not in y).
    # Reverse order to get inverse diff.
    second = set(second)
    return [item for item in first if item not in second]


def dedupe_array(data, col):
    # provide column on which to match dupes (starts with 0)
    new_data = []
    for row in data:
        if row[col] not in [r[col] for r in new_data]:
            new_data.append(row)
    return new_data


def trim_array(data, indices):
    # provide column indexes as list to remove (starts with 0)
    # Leaves original array intact (by deep copying)
    new_data = copy.deepcopy(data)
    for row in new_data:
        for i in sorted(indices, reverse=True):
            del row[i]
    return new_data


def sort_array(data, match_key=0, ignore_heads=False):
    # Sort an array based on given column (1st one by default)
    data_sorted = copy.deepcopy(data)
    if ignore_heads:
        heads = data_sorted.pop(0)
    data_sorted.sort(key=lambda x: x[match_key])
    if ignore_heads:
        data_sorted.insert(0, heads)
    return data_sorted
