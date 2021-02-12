import subprocess
from configparser import ConfigParser
import os
import pickle
import requests


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


def saxon_process(saxonPath, inFile, transformFile, outFile, theParams=" "):
    # Process an XSLT transformation. Use None for outFile to send to stdout.
    if outFile:
        outStr = " > " + outFile
    else:
        outStr = " "
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
    if result[1]:  # error
        return "SAXON MESSAGE: " + str(result[1].decode("utf-8"))
    else:
        return result[0].decode("utf-8")


def saxon_process2(saxonPath, inFile, transformFile, outFile, theParams=" "):
    # TODO: Test error parsing.
    # Process an XSLT transformation. Use None for outFile to send to stdout.
    if outFile:
        outStr = " > " + outFile
    else:
        outStr = " "
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


def jing_process(jingPath, filePath, schemaPath, compact=False):
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


def rsync_process(keyPath, fromPath, toPath, options):
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
    return get_status('https://clio.columbia.edu/catalog/' + str(bibid))


def diff(first, second):
    # Return list of x - y (everything in x that is not in y).
    # Reverse order to get inverse diff.
    second = set(second)
    return [item for item in first if item not in second]
