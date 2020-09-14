from Tools import PyVasp

import os.path


def parse_file(filename):
    """
    :param filename: filename of the file to read
    :return: Return the parser object corresponding to the filename extension
    """
    if not os.path.isfile(filename):
        raise Exception("The file ['%s'] does not exist" % filename)
    ext = os.path.splitext(filename)[1].lower()
    file = None

    if ext == ".log":
        # gaussian output
        # vasp output
        pass
    elif ext == ".xyz":
        pass

    elif ext == ".xml":
        file = PyVasp.Vasp(filename)

    elif filename == 'OUTCAR':
        file = PyVasp.Vasp(filename)

    if file is None:
        raise Exception("Error in parse_file for file ['%s']" % filename)
    return file
