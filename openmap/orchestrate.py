from openmap.databases import search_db

from configuration import ChemOs_CONFIG, Query

# NUM_TOTAL =   # len of the data base
BUDGET = 4  # how many experiment you want to perform
ChemOs_CONFIG_FILE = 'configuration/Optimizer_config.json'

# BATCH_SIZE = args.batch_size

seed = 3

BATCH_SIZE = ChemOs_CONFIG.get('general')['sampling_strategies']

campaign_name = ChemOs_CONFIG.get('parameters')[0]['name']
objective_name = ChemOs_CONFIG.get('objectives')[0]['name']

# Check if DB exit on maple server  if not  wrap data and create data DB

# download data  on database


data = search_db.get_pd_db(Query['criteria'], 'mp')

print(data.head(10))
