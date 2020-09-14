import numpy as np

from pymatgen.io.vasp.outputs import Vasprun
from pymatgen.io.vasp.outputs import BSVasprun
from pymatgen.io.vasp.outputs import Outcar

PROPERTIES = ["final_energy", "volume", "energy_per_atom"]


def get_property_names(name):
    """
    param:name:either usual name or operator name of a property
    return:( usual name, operator name ) of the property
    """
    if name in PROPERTIES:
        usname = name
    else:
        usname = None
    return usname


class Property(object):

    def __init__(self, res):
        """
        Param res:file class ( PyVASP, PyQchem ...)
        """
        self.res = res

    def get_property(self, name):
        """
        get any type of property
        param name:name of the property
        """
        # Get properties name and check it
        usname = get_property_names(name)

        if usname is None:  # invalid name
            print("Property [{}] not recognized".format(name))
            return None
        try:
            prop = eval("self.res.get_" + usname + "()")
            return prop
        except AttributeError:
            print("Property [{}] not implemented".format(usname))
            return None


class ListProperty(object):
    def __init__(self, files, keys=None):
        """
        :param files:list of file class
        :param keys: list of keys to be associated with each property
              if None, filename is used
        """
        self.files = files
        self.properties = {}
        for key, file in zip(self.keys, self.files):
            self.properties[key] = Property(file)

    def get_properties(self, name):
        """
        get any type of property
        :param name:name of the property or name
        """
        props = {}
        for key in self.properties:
            props[key] = self.properties[key].get_property(name)

        return props
