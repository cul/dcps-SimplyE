import pickle

def pickle_it(obj, path):
    """Save object as pickle file

    Args:
        obj (dict, list): Python object (e.g., dict) to pickle
        path (str): Path to output file
    """
    print("Saving pickle to " + str(path) + "...")
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def unpickle_it(path):
    """Unpickle a pickle file

    Args:
        path (str): Path to pickle to unpickle

    Returns:
        dict or list: The unpickled objects
    """
    print("Unpickling from " + str(path) + "...")
    with open(path, "rb") as f:
        output = pickle.load(f)
    return output
