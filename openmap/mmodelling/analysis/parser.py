import pathlib

from openmap.mmodelling.analysis import pyvasp
from openmap.computing.log import logger


def parse_file(filename):
    """
    :param filename: filename of the file to read
    :return: Return the parser object corresponding to the filename extension
    """
    file = None
    ext = None
    vasp_file = ['vasprun.xml', 'OUTCAR']
    if not pathlib.Path(filename).exists():
        logger.error('The Path  [{}] does not exist'.format(filename))
    # elif os.path.isfile(filename):
    elif pathlib.Path(filename).is_file():
        ext = pathlib.Path(filename).suffix
        # ext = os.path.splitext(filename)[1].lower()

    if ext == '.log':
        # gaussian output
        # vasp output
        pass
    elif ext == '.xyz':
        pass

    # elif ext == ".xml":
    #   file = pyvasp.ExtractVasp(filename)

    # elif filename == 'OUTCAR':
    #    file = pyvasp.ExtractVasp(filename)

    elif pathlib.Path(filename + '/OUTCAR').is_file() or pathlib.Path(filename + '/vasprun.xml').is_file():
        file = pyvasp.ExtractVasp(filename)

    if file is None:
        logger.error('Error in parse_file for file [{}]'.format(filename))
    return file
