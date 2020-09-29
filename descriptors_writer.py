#!/usr/bin/env python


import json


def generate_descriptors(json_name, df, features, struct_id='id'):
    """
    :param json_name: name of file to return
    :param df: pandas dataframe with features
    :param features: list of features
    :param struct_id: name of column  with molecule id
    :return: json file with descriptors
    """
    descriptors = {}

    for index, row in df.iterrows():
        data = {}
        for feature in features:
            data[feature] = row[feature]
        descriptors[row[struct_id]] = data

    with open('{}.json'.format(json_name), 'w') as fp:
        json.dump(descriptors, fp, indent=6)

# if __name__ == '__main__':
# generate_descriptors()
