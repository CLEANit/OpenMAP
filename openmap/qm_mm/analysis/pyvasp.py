import os
import re
from re import M as moultline
from re import compile

import numpy as np
from pymatgen.io.vasp.outputs import Vasprun

# from analysis import Constants

__all__ = ['ExtractVasp']


class ExtractVasp(object):
    """
    Vasprun: property that can be extract from Vasprum object
    ['as_dict', 'atomic_symbols', 'complete_dos', 'converged', 'converged_electronic', 'converged_ionic', 'dielectric',
    'dielectric_data', 'dos_has_errors', 'efermi', 'eigenvalue_band_properties', 'eigenvalues', 'epsilon_ionic',
    'epsilon_static', 'epsilon_static_wolfe', 'exception_on_bad_xml', 'filename', 'final_energy', 'final_structure',
    'get_band_structure', 'get_computed_entry', 'get_potcars', 'get_trajectory', 'hubbards', 'idos', 'incar',
    'initial_structure', 'ionic_step_offset', 'ionic_step_skip', 'ionic_steps', 'is_hubbard', 'is_spin', 'kpoints',
    'nionic_steps', 'occu_tol', 'optical_absorption_coeff', 'other_dielectric', 'parameters', 'pdos', 'potcar_spec',
    'potcar_symbols', 'projected_eigenvalues', 'run_type', 'structures', 'tdos', 'to_json',  'vasp_version']
    """

    def __init__(self, file_path):
        """

        :param file_path: path to the vaspout  file
        """
        self.file_path = file_path
        # self.vrun = self.read_vasprun_xml()

    def __outcar__(self):
        """Returns path to OUTCAR file.
        :raise IOError: if the OUTCAR file does not exist.
        """
        from os.path import exists, join

        path = join(self.file_path, 'OUTCAR')
        # name = pathlib.PurePathsel(self.file_path).name
        # path = self.file_path
        if not exists(path):
            raise IOError('Path {0} does not exist.\n'.format(path))
        return open(path, 'r')

    def _search_OUTCAR(self, regex, flags=0):
        """ Looks for all matches. """
        regex = compile(regex, flags)
        with getattr(self, self.__outcar__.__name__)() as file:
            if moultline & flags:
                for found in regex.finditer(file.read()):
                    yield found
            else:
                for line in file:
                    found = regex.search(line)
                    if found is not None:
                        yield found

    def _rsearch_OUTCAR(self, regex, flags=0):
        """ Looks for all matches starting from the end. """
        from re import M as moultline
        from re import compile

        regex = compile(regex)
        with getattr(self, self.__outcar__.__name__)() as file:
            lines = file.read() if moultline & flags else file.readlines()
        if moultline & flags:
            for v in [u for u in regex.finditer(lines)][::-1]:
                yield v
        else:
            for line in lines[::-1]:
                found = regex.search(line)
                if found is not None:
                    yield found

    def _find_first_OUTCAR(self, regex, flags=0):
        """ Returns first result from a regex. """
        for first in getattr(self, self._search_OUTCAR.__name__)(regex, flags):
            return first
        return None

    def _find_last_OUTCAR(self, regex, flags=0):
        """ Returns first result from a regex. """
        for last in getattr(self, self._rsearch_OUTCAR.__name__)(regex, flags):
            return last
        return None

    @property
    def ialgo(self):
        """ Returns the kind of algorithms. """
        # Look for line like:    IALGO  =     68    algorithm
        result = self._find_first_OUTCAR(r"""^\s*IALGO\s*=\s*(\d+)\s*""")
        return int(result.group(1))

    @property
    def algo(self):
        """ Returns the kind of algorithms. """
        # This could be gotten in OUTCAR: use the 1 occurance of:
        #   ALGO = Fast
        return {
            68: 'Fast',
            38: 'Normal',
            48: 'Very Fast',
            58: 'Conjugate',
            53: 'Damped',
            4: 'Subrot',
            90: 'Exact',
            2: 'Nothing',
        }[self.ialgo]

    @property
    def is_dft(self):
        """ True if this is a DFT calculation, as opposed to GW. """
        try:
            return self.algo not in ['gw', 'gw0', 'chi', 'scgw', 'scgw0']
        except BaseException:
            return False

    def _read_vasprun_xml(self):
        try:
            return Vasprun(os.path.join(self.file_path, 'vasprun.xml'))
        except BaseException:
            print('Unable to read the file [vasprun.xlm]')
            return None

    def get_final_energy(self):
        """
        :return: return final energy from vasp xlm file
        """
        try:
            vrun = self._read_vasprun_xml()
            if vrun.converged:
                return vrun.final_energy
            else:
                print('Calculation not  converged ')
                return None
        except BaseException:
            print('Unable to read final_energy ')
            return None

    def get_volume(self):
        """
        volume : 57.15385804647134
        :return: return volume of the final structure
        """
        vrun = self._read_vasprun_xml()

        try:
            composition = vrun.final_structure.composition
            return composition.volume
        except BaseException:
            return None

    def get_energy_per_atom(self):
        """
        :return:  energy per atom
        """

        vrun = self._read_vasprun_xml()
        composition = vrun.final_structure.composition
        return vrun.final_energy / composition.num_atoms

    def get_lattice_parameter(self):
        """
        abc : 3.77661336 4.00860231 3.77528771
        :return:  array with abc paramaters
        """
        vrun = self._read_vasprun_xml()

        return vrun.final_structure.abc

    def get_lattice_matrix(self):
        """
        A : 3.77661336 0.0 0.0
        B : -0.0 4.00860231 0.0
        C : 0.0 0.0 3.77528771
        :return:  array with abc paramaters
        """
        vrun = self._read_vasprun_xml()
        A = vrun.final_structure.A
        B = vrun.final_structure.B
        C = vrun.final_structure.C
        return np.array(A, B, C)

    # def get_final_structure(self):
    #     """
    #     Gets the final structure from the simulation
    #
    #     Returns:
    #        atoms.Atoms: The final structure
    #
    #     """
    #
    #     try:
    #         basis = self.get_initial_structure()
    #         basis.set_cell(self.vrun.as_dict["final_structure"]["cell"])
    #         positions = self.vrun.as_dict["final_structure"]["positions"]
    #         if len(positions[positions > 1.01]) > 0:
    #             basis.positions = positions
    #         else:
    #             basis.set_scaled_positions(positions)
    #         return basis
    #     except (KeyError, AttributeError, ValueError):
    #         return

    # def get_final_structure_from_file(self, filename="CONTCAR"):
    #     """
    #     Get the final structure of the simulation usually from the CONTCAR file
    #
    #     Args:
    #         filename (str): Path to the CONTCAR file in VASP
    #
    #     Returns:
    #         pyiron.atomistics.structure.atoms.Atoms: The final structure
    #     """
    #     filename = posixpath.join(self.working_directory, filename)
    #     if self.structure is None:
    #         try:
    #             output_structure = read_atoms(filename=filename)
    #             input_structure = output_structure.copy()
    #         except (IndexError, ValueError, IOError):
    #             raise IOError("Unable to read output structure")
    #     else:
    #         input_structure = self.structure.copy()
    #         try:
    #             output_structure = read_atoms(
    #                 filename=filename,
    #                 species_list=input_structure.get_parent_symbols(),
    #             )
    #             input_structure.cell = output_structure.cell.copy()
    #             input_structure.positions[
    #                 self.sorted_indices
    #             ] = output_structure.positions
    #         except (IndexError, ValueError, IOError):
    #             raise IOError("Unable to read output structure")
    #     return input_structure

    # def get_magnetic_structure(job):
    #     basis = Atoms().from_hdf(job["input"])
    #     magmons = basis.get_initial_magnetic_moments()
    #     if all(magmons == None):
    #         return {"magnetic_structure": "non magnetic"}
    #     else:
    #         abs_sum_mag = sum(np.abs(magmons))
    #         sum_mag = sum(magmons)
    #         if abs_sum_mag == 0 and sum_mag == 0:
    #             return {"magnetic_structure": "non magnetic"}
    #         elif abs_sum_mag == np.abs(sum_mag):
    #             return {"magnetic_structure": "ferro-magnetic"}
    #         elif abs_sum_mag > 0 and sum_mag == 0:
    #             return {"magnetic_structure": "para-magnetic"}
    #         else:
    #             return {"magnetic_structure": "unknown"}
    # @property
    # def get_magnectic_moments(self):
    #     """
    #     read Total magnectic moment from OUTCAR file
    #
    #     magnetization (x)
    #
    #     # of ion s p d tot
    #     ----------------------------------------
    #     1 .000 .012 .000 .012
    #     32 .001 .010 .000 .011
    #
    #
    #     33 .218 .034 2.105 2.357
    #     ------------------------------------------------
    #     tot .227 .209 2.105 2.542
    #
    #     :return: Returns magnetic moment from OUTCAR.
    #     """
    #
    #     f = open(os.path.join(self.file_path, 'OUTCAR'), 'r')
    #     lines = f.readlines()
    #     f.close()
    #
    #     for iline, line in enumerate(lines):
    #         if
    #     B = atoms.get_magnetic_moment()  # Total magnetic moment
    #     magmoms = atoms.get_magnetic_moments() #Magnetic moments
    #     return B

    # @property
    # def get_bandgap(self, location=None, tol=1e-3):
    #     """
    #     read the bandgap from DOSCAR
    #     :param location: path to DOSCAR
    #     :param tol:
    #     Condunction Band Minimum  and Valence Band Maximum
    #     :return: "Gap, VBM, CBm"
    #     """
    #     if location is None:
    #         location = os.path.join(self.file_path, 'OUTCAR')
    #
    #     doscar = open(location)
    #     for i in range(6):
    #         l = doscar.readline()
    #     efermi = float(l.split()[3])
    #     step1 = doscar.readline().split()[0]
    #     step2 = doscar.readline().split()[0]
    #     step_size = float(step2) - float(step1)
    #     not_found = True
    #     while not_found:
    #         l = doscar.readline().split()
    #         e = float(l.pop(0))
    #         dens = 0
    #         for i in range(len(l) / 2):
    #             dens += float(l[i])
    #         if e < efermi and dens > tol:
    #             bot = e
    #         elif e > efermi and dens > tol:
    #             top = e
    #             not_found = False
    #     if top - bot < step_size * 2:
    #         return 0, 0, 0
    #     else:
    #         # return top - bot,bot-efermi,top-efermi
    #         return top - bot, bot, top

    @property
    def get_total_energy(self):
        """ Greps total energy from OUTCAR."""
        if not self.is_dft:
            raise AttributeError('not a DFT calculation.')
        regex = """energy\\s+without\\s+entropy=\\s*(\\S+)\\s+energy\\(sigma->0\\)\\s+=\\s+(\\S+)"""
        result = self._find_last_OUTCAR(regex)
        if result is None:
            print('Could not find energy in OUTCAR')
        return float(result.group(1))  # energy in  eV

    @property
    def get_fermi_energy(self):
        """ Greps fermi energy from OUTCAR. """
        if not self.is_dft:
            raise AttributeError('not a DFT calculation.')
        regex = r"""E-fermi\s*:\s*(\S+)"""
        result = self._find_last_OUTCAR(regex)
        if result is None:
            # raise Exception("Could not find fermi energy in OUTCAR")
            print('Could not find fermi energy in OUTCAR')
        return float(result.group(1))  # energy in  eV

    @property
    def moment(self):
        """
        Returns Initial magnetic moment from OUTCAR.

        number of electron     192.0000000 magnetization      28.0000000
        """
        if not self.is_dft:
            # raise AttributeError('not a DFT calculation.')
            print('not a DFT calculation.')
        regex = r"""^\s*number\s+of\s+electron\s+(\S+)\s+magnetization\s+(\S+)\s*$"""
        result = self._find_last_OUTCAR(regex)
        if result is None:
            print('Could not find magnetic moment in OUTCAR')
        return float(result.group(2))

    def _partial_charges_impl(self, grep):
        """Greps partial charges from OUTCAR.
        This is a numpy array where the first dimension is the ion (eg one row
        per ion), and the second the partial charges for each angular momentum.
        The total is not included. Implementation also used for magnetization.
        The OUTCAR looks like the following, although in some
        cases there may be an extra column for the f shell,
        or the d shell may be missing.
         total charge
        # of ion     s       p       d       tot
        ----------------------------------------
          1        0.288   0.363   6.223   6.874
          2        1.771   4.143   0.000   5.914
        ------------------------------------------------
        tot        2.059   4.506   6.223  12.788
         magnetization (x)
        # of ion     s       p       d       tot
        ----------------------------------------
          1       -0.017  -0.008  -1.935  -1.960
          2       -0.005  -0.006   0.000  -0.011
        ------------------------------------------------
        tot       -0.022  -0.014  -1.935  -1.970
        """

        result = []
        with self.__outcar__() as file:
            lines = file.readlines()
        found = re.compile(grep)
        for index in range(1, len(lines) + 1):
            if found.search(lines[-index]) is not None:
                break
        if index == len(lines):
            return None
        index -= 4
        line_re = re.compile(r"""^\s*\d+((\s+\S+)+)\s*$""")
        for i in range(0, index):
            match = line_re.match(lines[-index + i])
            if match is None:
                break
            stgs = match.group(1).split()
            stgs = stgs[:-1]  # omit the last column, "tot"
            vals = [float(stg) for stg in stgs]
            result.append(vals)
        return np.array(result, dtype='float64')

    @property
    def get_magnetization(self):
        """Greps partial charges from OUTCAR.
        This is a numpy array where the first dimension is the ion (eg one row
        per ion), and the second the partial charges for each angular momentum.
        The total is not included.
        """
        if not self.is_dft:
            raise AttributeError('not a DFT calculation.')
        return self._partial_charges_impl(r"""^\s*magnetization\s*\(x\)\s*$""")

    @property
    def get_total_magnetization(self):
        """
        Returns magnetic moment from OUTCAR.

        The OUTCAR looks like the following, although in some
        cases there may be an extra column for the f shell,
        or the d shell may be missing.

         magnetization (x)
        # of ion     s       p       d       tot
        ----------------------------------------
          1       -0.017  -0.008  -1.935  -1.960
          2       -0.005  -0.006   0.000  -0.011
        ------------------------------------------------
        tot       -0.022  -0.014  -1.935  -1.970
        """
        magnetic_moment = self.get_magnetization

        return sum(sum(magnetic_moment))
