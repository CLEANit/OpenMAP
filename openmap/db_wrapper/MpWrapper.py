import pandas as pd
# from matminer.featurizers.composition import ElementFraction

from openmap.log import logger
from pymatgen import MPRester  # Composition


class MpWrapper(object):
    """
    wrap data on Materials project
    adapted from https://workshop.materialsproject.org/lessons/04_materials_api/api_use/
    """

    def __init__(self):
        pass

    # @staticmethod
    # def _featurizing_composition(data_df, formula='pretty_formula'):
    #     """
    #     Create pymatgen composition object from formula
    #     create feature with periodic table element
    #     :param data_df:
    #     :param formula:  name of the column with formula
    #     :return: date frame
    #     """
    #
    #     df = data_df.copy()
    #     df['composition'] = df.apply(
    #         lambda x: Composition(x['full_formula']), axis=1)
    #
    #     # ef = ElementFraction()
    #     # df = ef.featurize_dataframe(df, "composition")
    #
    #     # drop redundant information
    #     df = df.drop(
    #         columns=[
    #             'elements',
    #             'nelements',
    #             'hubbards',
    #             'spacegroup',
    #             'is_compatible',
    #             'pretty_formula',
    #             'icsd_ids',
    #             'icsd_id',
    #             'tags',
    #             'cif',
    #             'full_formula',
    #             'is_hubbard',
    #         ]
    #     )
    #     df = df.rename(columns={'material_id': 'id'})
    #     # df = df.drop(df.std()[df.std() <= threshold].index.values, axis=1)
    #     return df

    def wrap_mp(self, query):
        """
        mpr.query('{Li,Na,K,Rb,Cs}-N', ['material_id', 'pretty_formula'])
        :param query:
        :return: dataframe
        """
        mpr = MPRester()
        all_prop = list(mpr.supported_properties)
        all_prop.append('full_formula')
        logger.info('Wrapping data on the Open Materials Project Database')
        try:
            data = list(mpr.query(query, all_prop))
            df = pd.DataFrame.from_dict(data)
            # df = self._featurizing_composition(df)
            df['source'] = 'mp'
            return df
        except Exception as e:
            raise Exception(e)


if __name__ == '__main__':
    mp = MpWrapper()
    q = '{Li,Na,K,Rb,Cs}-N'

    data = mp.wrap_mp(q)
    print(data.head())
    print(data.columns.values)
