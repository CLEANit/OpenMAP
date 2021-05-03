import pandas as pd

from openmap.util.log import logger
from pymatgen import MPRester


class MpWrapper(object):
    """
    wrap data on Materials project
    adapted from https://workshop.materialsproject.org/lessons/04_materials_api/api_use/
    """

    def __init__(self):
        pass



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
