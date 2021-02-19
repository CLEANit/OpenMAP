import numpy as np
import pandas as pd
import itertools
# from openmap.databases.mp.MpWrapper import MpWrapper
# from openmap.databases.oq.OqWrapper import OqWrapper

from openmap.databases import MpWrapper
from openmap.databases import OqWrapper
from openmap.databases import NomadWrapper


def parse_input(el_set, db):
    """
    :param el_set: String of elements. eg {Ni,Mn,Cu,Co}-O.
    :param db: String, one of 'mp','oq','nomad'.

    for materials project no changes needed.
    for open quantum replace curly brackets with regular
        and '-' with ','.
    for nomad, returns a list of the elements, split at '-'.
    """
    # materials project
    if db == 'mp':
        return el_set
    
    # open quantum
    if db == 'oq':
        """
        '-' means OR
        ',' means AND 
        """
        for key, value in {'{': '(', '}': ')'}.items():
            el_set = el_set.replace(key, value)
            el_set = el_set.replace(key,value)

        # change '-' for ',' and  ',' for '-'
        indexC = [x for x, v in enumerate(el_set) if v == ',']
        indexD = [x for x, v in enumerate(el_set) if v == '-']
        el_set = list(el_set)
        for ind in indexC:
            el_set[ind] = '-'
        for ind in indexD:
            el_set[ind] = ','
        el_set = ''.join(el_set)
        return el_set
    # nomad
    if db == 'nomad':
        # going to search for all the elements and then replace

        el_set = el_set.replace('{','').replace('}','').split('-')

        return el_set
    return -1



def get_pd_db(el_set, db):
    el_set = parse_input(el_set, db)
    print(el_set)
    data_df = pd.DataFrame()
    if db == 'nomad':
        # will need to do a general query and parse through it 
        numb_el = len(el_set)
        # el_set[0].split(','), el_set[1].split(',')
        
        # get 
        all_el = list(itertools.product(
            *[s.split(',') for s in el_set]
        ))

        
        for atms in all_el:
            nwrap = NomadWrapper().search_params(atoms = list(atms), only_atoms=True)
            data_df = data_df.append(nwrap.get_pd_df())

        # parse through to get all entries with only numb_el elements
    elif db=='oq':
        qry = {
            'element_set':el_set
        }
        mpwrap = OqWrapper()
        data_df = mpwrap.wrap_oq(qry)

    elif db == 'mp':
        mpwrap = MpWrapper()
        data_df = mpwrap.wrap_mp(el_set)
    
    return data_df




def get_all(el_set):
    """
    Searches through all supported databases for data required.
    :param el_set: The element set. ex {Ag}-O
    :return:
    """
    dbs = ['oq','mp', 'nomad']

    df = pd.DataFrame(columns= ['composition'])
    for db in dbs:
        db_ret = get_pd_db(el_set, db)
        df = df.merge(db_ret, how = 'outer')


    # db_ret = get_pd_db(el_set, 'oq')
    # oq_db = get_pd_db(el_set, 'oq')
    # print(oq_db.shape)



    return df
class Controller:
    def __init__(self,mdb_conf):
        """
        :param mdb_conf: path to mdd config file
        """
        self.mdb = mdbControl(mdb_conf)

    def get_data(self, query):
        """
        "Smart" query. Will look in the database for query. If ~anything~ found, will return. 
        If nothing found, will query other implemented databases and add them to mdb. 
        """
        try:
            mdb_query = self.mdb.search(query)

            if len(mdb_query)>0:
                return mdb_query
            else:
                # search external dbs, and push those to ours before returning

                external_query = get_all(query)

                self.mdb.add_query(external_query)
                return external_query

        except Exception as e:
            logging.log(f'Exception raised in Controller. info: {e}')
            raise e
            
        






if __name__ == '__main__':

    a = '{Ni,Ag}-O'

    # print(parse_input(a, 'nomad'))


    get_pd_db(a, 'oq')
    # print(ret.columns.values)
    # print(ret.dtypes)
    # ret = get_pd_db(a, 'oq').head()
    # print(ret.columns.values)

    # ret =get_pd_db(a, 'mp').head()
    # print(ret.columns.values)


# n = NomadWrapper().search_params(atoms = ['Al', 'Ag', 'O'],crystal_system=[ 'ternary'])
# print(n.get_pd_df().head())


# qry = '{Ni,Mn,Cu,Co}-O'
# mpwrap = MpWrapper()
# data_df = mpwrap.wrap_mp(qry)
# print(data_df.head())



# example running oqwrapper
# qry = {
#         "element_set": "(Fe-Mn),O", # composition include (Fe OR Mn) AND O
#         "limit": 100
#     }
# mpwrap = OqWrapper()
# data_df = mpwrap.wrap_oq(qry)
# print(data_df.head())


