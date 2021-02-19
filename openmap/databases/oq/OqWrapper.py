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
        pass

    @staticmethod
    def _featurizing_composition(data_df):
        """
        Create pymatgen composition object from formula
        create feature with periodic table element
        :param df:
        :param formula:  name of the column with formula
        :return: date frame
        """

        data_df['composition'] = data_df.apply(lambda x: Composition(x['name']), axis=1)
        
        # ef = ElementFraction()
        # df = ef.featurize_dataframe(df, "composition")
        data_df = data_df.rename(columns={'entry_id': 'id'})

        data_df = data_df.drop(columns =['name','natoms','spacegroup','ntypes','composition_generic','formationenergy_id',
                            'prototype','unit_cell','sites','stability','fit','calculation_label','duplicate_entry_id',
                            'calculation_id', 'icsd_id'])

        # df = df.drop(df.std()[df.std() <= threshold].index.values, axis=1)
        return data_df

    def wrap_oq(self, query):
        """
        element_set": "(Fe-Mn),O",  # composition include (Fe OR Mn) AND O
        :param query:
        :return: dataframe
        """
        # oqr = qr.QMPYRester()
        logger.info('Wrapping data on the Open Quantum Database')
        try:
            with qr.QMPYRester() as q:
                data = q.get_oqmd_phases(verbose=False, **query)
                df = pd.DataFrame.from_dict(data['data'])
                df = self._featurizing_composition(df)

                df = df.astype({'id':'string'})
                df['source']='oq'
                return df
        except Exception as e:
            logger.info('Error in OqWrapper. ')
            raise Exception(e)

if __name__=='__main__':
    
    qry = {
        'element_set': '(Fe-Mn),O',                    # include element Fe and Mn
        }
    mpwrap = OqWrapper()
    data_df = mpwrap.wrap_oq(qry)
    # print(data_df.head())
    # print(data_df.info(verbose=True))
    print(data_df.head())
