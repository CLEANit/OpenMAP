#!/usr/bin/env python

import os
import copy
import json
import pickle
import numpy as np


# =================================================================

class CategoryWriter(object):

    def __init__(self, project_name, descriptors):
        self.project_name = project_name
        self.descriptors = descriptors
        self.json_file = None
        self.opts = None
        self.desc_names = {self.project_name: self.descriptors}
        self.param_names = [self.project_name]

    def generate_descriptors(self, df, features=None, struct_id='id', json_name=None):
        """
        :param json_name: name of file to return
        :param df: pandas dataframe with features
        :param features: list of features
        :param struct_id: name of column  with molecule id
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
            descriptors[row[struct_id]] = data

        with open('{}.json'.format(json_name), 'w') as fp:
            json.dump(descriptors, fp, indent=6)

    def write_categories(self, home_dir, with_descriptors=True):
        self.json_file = json.loads(open('{}.json'.format(self.project_name), 'r').read())
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

            cat_details_file = '{}cat_details_{}.pkl'.format(dir_name, param_name)
            with open(cat_details_file, 'wb') as content:
                pickle.dump(opt_list, content)


# =================================================================

if __name__ == '__main__':
    cat_writer = CatWriter()
    cat_writer.write_cats('./')
