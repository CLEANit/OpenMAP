import numpy as np
from openmap.util.log import logger
from pymatgen.io.vasp.outputs import BSVasprun, Outcar, Vasprun

PROPERTIES = {
    'final_energy': 'final_energy',
    'volume': 'volume',
    'energy_per_atom': 'energy_per_atom',
    'total_magnetization': 'total_magnetization',
    'fermi_energy': 'fermi_energy',
    'Lattice constant': 'abc',
    'bulk modulus': 'B',
    'elastic constants': 'E',
    'Vacancy formation energy': 'V_energy',
    'Interstitial formation energy': 'Interstitial_energy',  # Both octahedral and tetrahedral
    'Stacking fault energies': 'Stacking_fault_energies',  # Extrinsic and intrinsic stacking fault energies
    'Surface formation energies': 'Surface_energies',
    'E-V plot': 'E-V plot',
    'GSF plot': 'GSF plot',
    'Nudged Elastic Band': 'Nudged Elastic Band'

}


class Property(object):
    def __init__(self, res):
        """
        Param res:file class ( PyVASP, PyQchem ...)
        """
        self.res = res

    def get_property_names(self, name):
        """
        param:name:either usual name or operator name of a property
        return:( usual name, operator name ) of the property
        """
        if name in PROPERTIES.keys():
            usname = PROPERTIES[name]
        else:
            usname = None

        return usname

    def get_property(self, name):
        """
        get any type of property
        param name:name of the property
        """
        # Get properties name and check it

        usname = self.get_property_names(name)
        if usname is None:  # invalid name
            logger.error('Property [{}] not recognized'.format(name))
            return None
        try:
            prop = eval('self.res.get_' + usname)
            return prop
        except Exception as err:
            logger.error(f'{err}')
            return None
