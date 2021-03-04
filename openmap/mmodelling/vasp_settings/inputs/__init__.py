import os

import yaml

vs_path = os.path.dirname(os.path.abspath(__file__))
VASP_SETTINGS = {}
for f in os.listdir(vs_path):
    if 'yml' not in f:
        continue
    settings = yaml.safe_load(open('{}/{}'.format(vs_path, f)).read())
    VASP_SETTINGS[f.replace('.yml', '')] = settings
