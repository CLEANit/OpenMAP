import itertools
from matminer.featurizers.composition import ElementFraction
from pymatgen import Composition
import numpy as np
import pandas as pd
from openmap.data_wrapper import MpWrapper, OqWrapper, NomadWrapper
from openmap.util.log import logger

todrop = {'mp': ['full_formula',
                 ['elements', 'nelements', 'hubbards', 'spacegroup', 'is_compatible', 'pretty_formula', 'icsd_ids',
                  'icsd_id', 'tags', 'cif', 'full_formula', 'is_hubbard', 'nsites', 'energy', 'volume',
                  'unit_cell_formula', 'e_above_hull', 'task_ids', 'oxide_type', 'source', 'composition']],
          'oq': ['name',
                 ['name',
                  'natoms',
                  'spacegroup',
                  'ntypes',
                  'composition_generic',
                  'formationenergy_id',
                  'prototype',
                  'unit_cell',
                  'sites',
                  'stability',
                  'fit',
                  'calculation_label',
                  'duplicate_entry_id',
                  'calculation_id',
                  'icsd_id',
                  'composition'
                  ]]}


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
            el_set = el_set.replace(key, value)

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

        el_set = el_set.replace('{', '').replace('}', '').split('-')

        return el_set
    return -1


def get_pd_db(el_set, db):
    el_set = parse_input(el_set, db)
    logger.info(f'Campaign Query: {el_set}')
    data_df = pd.DataFrame()
    if db == 'nomad':
        # will need to do a general query and parse through it
        numb_el = len(el_set)
        # el_set[0].split(','), el_set[1].split(',')

        # get
        all_el = list(itertools.product(*[s.split(',') for s in el_set]))

        for atms in all_el:
            nwrap = NomadWrapper().search_params(atoms=list(atms), only_atoms=True)
            data_df = data_df.append(nwrap.get_pd_df())

        # parse through to get all entries with only numb_el elements
    elif db == 'oq':
        qry = {'element_set': el_set}
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
    dbs = ['oq', 'mp', 'nomad']

    df = pd.DataFrame(columns=['composition'])
    for db in dbs:
        db_ret = get_pd_db(el_set, db)
        df = df.merge(db_ret, how='outer')

    # db_ret = get_pd_db(el_set, 'oq')
    # oq_db = get_pd_db(el_set, 'oq')
    # print(oq_db.shape)

    return df


def featurizing_composition(data_df, db, threshold=0.01):
    """
    Create pymatgen composition object from formula
    create feature with periodic table element
    :param threshold: drop column with std <
    :param db: name of the data base
    :param data_df:
    :return: dataframe
    """
    formula = todrop[db][0]  # column to drop
    drop = todrop[db][1]  # name of the column with formula
    df = data_df.copy()
    df['composition'] = df.apply(
        lambda x: Composition(x[formula]), axis=1)

    ef = ElementFraction()
    df = ef.featurize_dataframe(df, "composition")

    # drop redundant information
    df = df.drop(columns=drop)
    # df = df.rename(columns={'material_id': 'id'})
    df = df.drop(df.std()[df.std() <= threshold].index.values, axis=1)
    return df


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
