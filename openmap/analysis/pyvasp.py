import numpy as np
from pymatgen.io.vasp.outputs import Vasprun


# from analysis import Constants

class Vasp(object):
    """

    """

    def __init__(self, filename='vasprun.xml'):
        self.filename = filename

    def get_final_energy(self):
        """
        :return: return final energy from vasp xlm file
        """
        try:
            vrun = Vasprun(self.filename)
            return vrun.final_energy
        except:
            print("Unable to read final_energy in {}".format(self.filename))
            return None

    def get_volume(self):
        """
        volume : 57.15385804647134
        :return: return volume of the final structure
        """
        vrun = Vasprun(self.filename)
        composition = vrun.final_structure.composition

        return composition.volume

    def get_energy_per_atom(self):
        """
        :return:  energy per atom
        """

        vrun = Vasprun(self.filename)
        composition = vrun.final_structure.composition
        return vrun.final_energy / composition.num_atoms

    def get_lattice_parameter(self):
        """
        abc : 3.77661336 4.00860231 3.77528771
        :return:  array with abc paramaters
        """
        vrun = Vasprun(self.filename)

        return vrun.final_structure.abc

    def get_lattice_matrix(self):
        """
        A : 3.77661336 0.0 0.0
        B : -0.0 4.00860231 0.0
        C : 0.0 0.0 3.77528771
        :return:  array with abc paramaters
        """
        vrun = Vasprun(self.filename)
        A = vrun.final_structure.A
        B = vrun.final_structure.B
        C = vrun.final_structure.C
        return np.array(A, B, C)
