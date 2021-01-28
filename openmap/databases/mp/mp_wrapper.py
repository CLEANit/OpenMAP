import pandas as pd
from matminer.featurizers.composition import ElementFraction
from pymatgen import Composition, MPRester
from openmap.computing.log import logger


class MpWrapper(object):
    """
     wrap data on Materials project
     adapted from https://workshop.materialsproject.org/lessons/04_materials_api/api_use/
    """

    def __init__(self):
        x = None

    @staticmethod
    def _featurizing_composition(data_df, formula='pretty_formula'):
        """
        Create pymatgen composition object from formula
        create feature with periodic table element
        :param data_df:
        :param formula:  name of the column with formula
        :return: date frame
        """

        df = data_df.copy()
        ef = ElementFraction()
        df['composition'] = df.apply(lambda x: Composition(x['composition']), axis=1)
        df = ef.featurize_dataframe(df, "composition")
        # df = df.drop(df.std()[df.std() <= threshold].index.values, axis=1)
        return df

    def wrap_mp(self, query):
        """
        mpr.query('{Li,Na,K,Rb,Cs}-N', ['material_id', 'pretty_formula'])
        :param query:
        :return: dataframe
        """
        mpr = MPRester()
        all_prop = mpr.supported_properties
        all_prop.append('full_formula')
        logger.info('Wrapping data on the Open Materials Project  Database')
        try:
            data = mpr.query(query, all_prop)
            df = pd.DataFrame.from_dict(data)
            df = self._featurizing_composition(df)
            return df
        except Exception as e:
            raise Exception(e)
