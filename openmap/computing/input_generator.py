from ase.io import read, jsonio
from ase.utils import PurePath
import subprocess
from pymatgen import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.io.vasp.inputs import Poscar
from pymatgen.io.vasp.inputs import Potcar
from pymatgen.io.vasp.inputs import Kpoints
from pymatgen.io.vasp.inputs import Incar

import os
from pathlib import Path
from openmap.computing.log import logger
from openmap.configuration.vasp_settings import POTENTIALS, VASP_SETTINGS
import copy
import shutil
vasp_calculations = {"static": 'static',
                     "relaxation": 'relaxation',
                     'magnetization': 'magmom'}


class InputGenerator(object):
    def __init__(self, local_path, software='vasp'):
        """

        :param job_dir: name for the imput dir
        :param structure: pymatgen structure object
        :param properties:
        :param software:
        """
        self.software = software
        self.local_path = local_path
        self.make_workdir()


    def make_workdir(self):

        try:
            Path(self.local_path).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            if 'already exists' in e:
                logger.info(f'Working directory {self.local_path} already exists')
            else:
                logger.error(f'{e}')
        else:
            logger.info(f'Working directory [{self.local_path}] created successfully')
        #

    @logger.catch
    def vasp_input_from_structure(self, job_names, structures, properties):
        vasp_input = self.software + '_input'
        setting_file = vasp_calculations[properties]
        settings = VASP_SETTINGS[setting_file]

        potential = POTENTIALS[settings['potentials']]
        potential = potential['elements']
        incar_dict = copy.deepcopy(settings)
        del incar_dict['potentials']
        del incar_dict['hubbards']
        del incar_dict['magnetism']

        # POTENTIALS
        input_path = []
        for job_name, structure in zip(job_names, structures):
            input_dir = os.path.join(self.local_path, job_name, vasp_input)
            Path(input_dir).mkdir(parents=True, exist_ok=True)
            basis_set = [potential[element] for element in structure.symbol_set]
            #
            poscar = Poscar(structure=structure)
            incar = Incar(incar_dict)
            potcar = Potcar(symbols=basis_set, functional='PBE_54')
            kpoints = Kpoints.monkhorst_automatic(kpts=(8, 8, 8), shift=(0.0, 0.0, 0.0))

            poscar.write_file(os.path.join(input_dir, 'POSCAR'))
            incar.write_file(os.path.join(input_dir, 'INCAR'))
            potcar.write_file(os.path.join(input_dir, 'POTCAR'))
            kpoints.write_file(os.path.join(input_dir, 'KPOINT'))
            shutil.make_archive(input_dir, 'tar', os.path.join(self.local_path, job_name))
            shutil.rmtree(input_dir, ignore_errors=True)
            input_path.append(os.path.join(self.local_path, job_name))

        logger.info(f'vasp inputs created successfully in [{self.local_path}]')
        return input_path
