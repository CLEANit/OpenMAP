import copy
import json
import os
import pickle

import numpy as np
from pathlib import Path
from openmap.util.log import logger


# =================================================================


class CategoryWriter(object):
    """

    """

    def __init__(self, project_name, descriptors):
        self.project_name = project_name
        self.descriptors = descriptors
        self.json_file = None
        self.opts = None
        self.desc_names = {self.project_name: self.descriptors}
        self.param_names = [self.project_name]

    def generate_descriptors(self, df, id_colm='material_id', features=None):
        """
        :param json_name: name of file to return
        :param df: pandas dataframe with features
        :param features: list of features
        :param id_colm: name of column  with molecule id
        :return: json file with descriptors
        """
        if features is None:
            features = self.descriptors
        descriptors = {}

        for index, row in df.iterrows():
            data = {}
            for feature in features:
                data[feature] = row[feature]
            descriptors[row[id_colm]] = data
        loc = Path(__file__).absolute().parent.parent
        Path(os.path.join(loc, 'campaign/{}'.format(self.project_name))).mkdir(parents=True, exist_ok=True)
        filepath = os.path.join(loc, 'campaign/{}/{}.json'.format(self.project_name, self.project_name))

        with open(filepath, 'w') as fp:
            json.dump(descriptors, fp, indent=6)
        logger.info('Descriptors dumped in  "{}.json" '.format(self.project_name))
        # if len(descriptors) != 0:
        #     logger.info(f'Generation of descriptors completed')

    def write_categories(self, with_descriptors=True):
        loc = Path(__file__).absolute().parent.parent
        jsonpath = os.path.join(loc, 'campaign/{}/{}.json'.format(self.project_name, self.project_name))
        self.json_file = json.loads(
            open(jsonpath, 'r').read())
        self.opts = {self.project_name: self.json_file}
        for param_name in self.param_names:
            opt_list = []
            for opt_name, opt_desc_dict in self.opts[param_name].items():
                opt_dict = {'name': opt_name}
                if with_descriptors:
                    opt_dict['descriptors'] = np.array(
                        [float(opt_desc_dict[desc_name])
                         for desc_name in self.desc_names[param_name]]
                    )
                opt_list.append(copy.deepcopy(opt_dict))

            # create cat details dir if necessary
            loc = Path(__file__).absolute().parent.parent
            dir_name = Path(os.path.join(loc, 'campaign/CatDetails'))
            # dir_name.mkdir(parents=True, exist_ok=True)
            try:
                dir_name.mkdir(parents=True, exist_ok=False)
            except FileExistsError:
                logger.info('Folder "CatDetails" is already there')
            else:
                logger.info('folder "CatDetails"  was created')

            cat_details_file = os.path.join(dir_name, 'cat_details_{}.pkl'.format(param_name))
            with open(cat_details_file, 'wb') as content:
                pickle.dump(opt_list, content)

            logger.info(
                f'Categories pickle in cat_details_{param_name}.pkl ')


# =================================================================


if __name__ == '__main__':
    cat_writer = CategoryWriter()
    cat_writer.write_cats()
