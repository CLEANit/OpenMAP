import copy
import os
import shutil
from pathlib import Path

from openmap.util.log import logger
from openmap.qm_mm.vasp.settings import POTENTIALS, VASP_SETTINGS, vasp_calculations
from pymatgen.io.vasp.inputs import Incar, Kpoints, Poscar, Potcar

__all__ = ['InputGenerator', "Software"]

Software = ['vasp', 'lammps']


class InputGenerator(object):
    def __init__(self, local_path):
        """
        :param local_path:
        :param software:
        """
        self.local_path = local_path
        self.make_workdir()

    def get_software_name(self, name):
        """
        param:name:name of softare
        return:
        """
        if name in Software:
            usname = name

        else:
            usname = None
        return usname

    def make_workdir(self):

        try:
            Path(self.local_path).mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            logger.info(
                f'Working directory [{self.local_path}] already exists')
        # else OSError as e :
        #       logger.error(f'{e}')
        else:
            logger.info(
                f'Working directory [{self.local_path}] created successfully')
        #

    def input_from_structure(self, job_names, structures, properties, software='vasp'):

        name = self.get_software_name(software)

        assert name is not None, f'[{name}] is not implemented'

        if name == 'vasp':
            return self.vasp_input_from_structure(job_names, structures, properties)

    @logger.catch
    def vasp_input_from_structure(self, job_names, structures, properties):
        setting_file = None
        vasp_input = 'vasp_input'
        try:
            setting_file = vasp_calculations[properties]
        except KeyError:
            logger.error(f'KeyError')

        assert setting_file is not None
        settings = VASP_SETTINGS[setting_file]

        potential = POTENTIALS[settings['potentials']]
        potential = potential['elements']
        incar_dict = copy.deepcopy(settings)
        #  TODO deal with  potential and hubbbards
        del incar_dict['potentials']
        del incar_dict['hubbards']
        # del incar_dict['magnetism']

        # POTENTIALS
        input_path = []
        for job_name, structure in zip(job_names, structures):
            input_dir = os.path.join(self.local_path, job_name, vasp_input)
            Path(input_dir).mkdir(parents=True, exist_ok=True)
            basis_set = [potential[element]
                         for element in structure.symbol_set]
            #
            poscar = Poscar(structure=structure)
            incar = Incar(incar_dict)
            potcar = Potcar(symbols=basis_set, functional='PBE_54')
            kpoints = Kpoints.monkhorst_automatic(
                kpts=(8, 8, 8), shift=(0.0, 0.0, 0.0))

            poscar.write_file(os.path.join(input_dir, 'POSCAR'))
            incar.write_file(os.path.join(input_dir, 'INCAR'))
            potcar.write_file(os.path.join(input_dir, 'POTCAR'))
            kpoints.write_file(os.path.join(input_dir, 'KPOINTS'))
            shutil.make_archive(input_dir, 'tar', os.path.join(
                self.local_path, job_name))
            shutil.rmtree(input_dir, ignore_errors=True)
            input_path.append(os.path.join(self.local_path, job_name))

        logger.info(f'vasp inputs created successfully in [{self.local_path}]')
        return input_path
