from pymatgen import MPRester
import pandas as pd

__version__ = '0.1'
__author__ = 'Conrard TETSASSI'
__maintainer__ = 'Conrard TETSASSI'
__email__ = 'ConrardGiresse.TetsassiFeugmo@nrc-cnrc.gc.ca'
__status__ = 'Development'


class FetchData(object):
    def __init__(self, criteria, properties):
        self.criteria = criteria
        self.properties = properties

    @property
    def wrap_mp(self):
        """
        Fetch data on Materials project
        :return:
        """
        mpr = MPRester()
        all_prop = mpr.supported_properties
        props = [prop for prop in self.properties if prop in all_prop]
        props.append('full_formula')
        for query in self.criteria:
            try:
                data = mpr.get_data(query)
                data_df = pd.DataFrame.from_dict(data)
                df = pd.concat([df, data_df])
            except:
                data = mpr.get_data(query)
                df = pd.DataFrame.from_dict(data)

        df = df[props]
        mp_ids = df['material_id'].to_list()
        df.insert(0, "map_id", mp_ids)

        return df
