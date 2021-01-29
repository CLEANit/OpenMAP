#!/usr/bin/env python
# -*- coding: utf-8 -*-


import qmpy_rester as qr
import pandas as pd
from matminer.featurizers.composition import ElementFraction
from pymatgen import Composition
from openmap.computing.log import logger


class OqWrapper(object):
    """
     wrap data on the Open Quantum Database
     adapted from https://github.com/mohanliu/qmpy_rester

     list of properties

     ['energy', 'energy_per_atom', 'volume', 'formation_energy_per_atom', 'nsites', 'unit_cell_formula',
     'pretty_formula', 'is_hubbard', 'elements', 'nelements', 'e_above_hull', 'hubbards', 'is_compatible',
     'spacegroup', 'task_ids', 'band_gap', 'density', 'icsd_id', 'icsd_ids', 'cif', 'total_magnetization',
     'material_id', 'oxide_type', 'tags', 'elasticity', 'full_formula']
    """

    def __init__(self):
        x = None

    @staticmethod
    def _featurizing_composition(data_df, formula='name'):
        """
        Create pymatgen composition object from formula
        create feature with periodic table element
        :param data_df:
        :param formula:  name of the column with formula
        :return: date frame
        """

        df = data_df.copy()
        ef = ElementFraction()
        df['composition'] = df.apply(lambda x: Composition(x['name']), axis=1)
        df = ef.featurize_dataframe(df, "composition")
        df.rename(columns={'entry_id': 'material_i'})
        # df = df.drop(df.std()[df.std() <= threshold].index.values, axis=1)
        return df

    def wrap_oq(self, query):
        """
        element_set": "(Fe-Mn),O",  # composition include (Fe OR Mn) AND O
        :param query:
        :return: dataframe
        """
        oqr = qr.QMPYRester()
        logger.info('Wrapping data on the Open Quantum Database')
        try:
            data = oqr.get_oqmd_phases(verbose=False, **query)
            df = pd.DataFrame.from_dict(data['data'])
            df = self._featurizing_composition(df)
            return df
        except Exception as e:
            raise Exception(e)


if __name__ == '__main__':
    qry = {
        "element_set": "(Fe-Mn),O", # composition include (Fe OR Mn) AND O
        "limit": 100

    }

    mpwrap = OqWrapper()

    data_df = mpwrap.wrap_oq(qry)

    print(data_df.head())
