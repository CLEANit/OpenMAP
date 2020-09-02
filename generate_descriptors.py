#!/usr/bin/env python

import os, sys
import glob
import json
from ase.db import connect

db = connect('/Users/ctetsass/Calculation_NRC/OpenMAPs/Data/Alloys/fcc_alloys.db')


def generate_descriptors():
    descriptors = {}

    for row in db.select():
        descriptors[row.id] = {'mass': row.mass,
                               'c_Al': row.c_Al,
                               'c_Au': row.c_Au,
                               'c_Cu': row.c_Cu,
                               'c_Ag': row.c_Ag,
                               'c_Pd': row.c_Pd,
                               'c_Pt': row.c_Pt,
                               'c_Ni': row.c_Ni}

    #print(descriptors)

    with open('alloys.json', 'w') as fp:
        json.dump(descriptors, fp, indent=6)


if __name__ == '__main__':
    generate_descriptors()
