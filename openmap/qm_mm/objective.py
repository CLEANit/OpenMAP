#!/usr/bin/env python
import os
import pathlib
import sys

import yaml
from openmap.qm_mm.analysis import parser
from openmap.qm_mm.analysis import Property
from openmap.computing.log import logger
from pymatgen.io.vasp.outputs import Vasprun

# logger = logging.getLogger(__name__)

# parser = argparse.ArgumentParser(description='Automated  Optimizer')
# # parser.add_argument('integers', metavar='N', type=int, nargs='+',
# #                    help='an integer for the accumulator')
# parser.add_argument('--prop',
#                     dest='property',
#                     type=str,
#                     default='',
#                     action='store',
#                     # required=True,
#                     help='objective of the campaign')
# args = parser.parse_args()


def job_converged(path):

    try:
        vrun = Vasprun(filename=os.path.join(path, 'vasp_output/vasprun.xml'))
        return vrun.converged
    except BaseException:
        return False


def get_objective(prop_name, file_path):
    objectives = []

    try:
        file = parser.parse_file(file_path)
        prop = Property(file)
        objectiv = prop.get_property(prop_name)
    except OSError as err:
        logger.error('OS error: {0}'.format(err))
        objectiv = None
    except Exception as err:
        logger.error('Exception error: {0}'.format(err))
        objectiv = None
    except BaseException:
        logger.error('Unable to read  {}'.format(file_path))
        objectiv = None
        pass

    return objectiv


if __name__ == '__main__':
    # loc = os.path.dirname(os.path.abspath(__file__))
    # loc = os.path.abspath(os.getcwd())
    # loc = pathlib.Path(__file__).parent.absolute() ## For the directory of
    # the script being run:
    loc = pathlib.Path().absolute()  # For the current working directory:
    prop_name = sys.argv[1]
    objective = {}
    # if job_converged(loc):
    try:
        prop = get_objective(prop_name, os.path.join(loc, 'vasp_output'))
        if prop is not None:
            objective[prop_name] = float(prop)
            logger.info(f'Successfully evaluated the [{prop_name}]')
        else:
            logger.error(f'Job not converged')
            objective[prop_name] = 5e-18
    except Exception as err:
        objective[prop_name] = 5e-18
        logger.error(f'{err}')
    # else:
    #     objective[prop_name] = 5E-18
    #     logger.error(f'Job not converged')

    file = open('objective.yml', 'w')
    yaml.dump(objective, file, default_flow_style=False)
    print(yaml.dump(objective))
    file.close()
    # with open('objective.yml', 'w') as outfile:
    #     yaml.dump(objective, outfile, default_flow_style=False)
