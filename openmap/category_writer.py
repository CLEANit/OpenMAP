#!/usr/bin/env python

import os
import copy
import json
import pickle
import numpy as np
from openmap.computing.log import logger

__version__ = '0.1'
__author__ = 'Conrard TETSASSI'
__maintainer__ = 'Conrard TETSASSI'
__email__ = 'ConrardGiresse.TetsassiFeugmo@nrc-cnrc.gc.ca'
__status__ = 'Development'


# =================================================================

class CategoryWriter(object):

    def __init__(self, project_name, descriptors):
        self.project_name = project_name
        self.descriptors = descriptors
        self.json_file = None
        self.opts = None
        self.desc_names = {self.project_name: self.descriptors}
        self.param_names = [self.project_name]

    def generate_descriptors(self, df, id_colm='map_id', features=None, json_name=None):
        """
        :param json_name: name of file to return
        :param df: pandas dataframe with features
        :param features: list of features
        :param id_colm: name of column  with molecule id
        :return: json file with descriptors
        """
        if features is None:
            features = self.descriptors
        if json_name is None:
            json_name = self.project_name

        descriptors = {}

        for index, row in df.iterrows():
            data = {}
            for feature in features:
                data[feature] = row[feature]
            descriptors[row[id_colm]] = data

        with open('{}.json'.format(json_name), 'w') as fp:
            json.dump(descriptors, fp, indent=6)

        if len(descriptors) != 0:
            logger.info(f'Generation of descriptors completed')

    def write_categories(self, home_dir, with_descriptors=True):
        self.json_file = json.loads(open('{}.json'.format(self.project_name), 'r').read())
        logger.info('The file [{}.json] has been created successfully'.format(self.project_name))
        self.opts = {self.project_name: self.json_file}
        for param_name in self.param_names:
            opt_list = []
            for opt_name, opt_desc_dict in self.opts[param_name].items():
                opt_dict = {'name': opt_name}
                if with_descriptors:
                    opt_dict['descriptors'] = np.array(
                        [float(opt_desc_dict[desc_name]) for desc_name in self.desc_names[param_name]])
                opt_list.append(copy.deepcopy(opt_dict))

            # create cat details dir if necessary
            dir_name = '{}CatDetails'.format(home_dir)
            if not os.path.isdir(dir_name):
                os.mkdir(dir_name)

            cat_details_file = '{}/cat_details_{}.pkl'.format(dir_name, param_name)
            with open(cat_details_file, 'wb') as content:
                pickle.dump(opt_list, content)

            logger.info(f'The file[{dir_name}/cat_details_{param_name}.pkl]  has been created successfully')


# =================================================================

if __name__ == '__main__':
    cat_writer = CatWriter()
    cat_writer.write_cats('./')
