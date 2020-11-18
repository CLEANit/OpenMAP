import configparser
import os
import yaml
import json
import pexpect, getpass

#from openmap.computing.resources import Host, Account, Project, Allocation, User


loc = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(loc, "Optimizer_config.json"), "r") as fr:
    ChemOs_CONFIG = json.load(fr)

with open(os.path.join(loc, "HPC_config.yml"), "r") as fr:
    HPC_CONFIG = yaml.safe_load(fr)

with open(os.path.join(loc, "DataBase_config.yml"), "r") as fr:
    DataBase_CONFIG = yaml.safe_load(fr)

with open(os.path.join(loc, "Query.yml"), "r") as fr:
    Query = yaml.safe_load(fr)


