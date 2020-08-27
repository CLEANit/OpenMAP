"""Remote host configuration."""
from os import environ, path
from dotenv import load_dotenv

# Load environment variables from .env
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

# Read environment variables
host = environ.get('cedar.computecanada.ca') # ('REMOTE_HOST')
user = environ.get('ctetsass') # ('REMOTE_USERNAME')
ssh_key_filepath = environ.get('~/.ssh') # ('SSH_KEY')
remote_path = environ.get('/home/ctetsass/scratch')# ('REMOTE_PATH')
passphrase = 'Gastipard_Isaro' # getpass.getpass()

local_file_directory = '/Users/ctetsass/Calculation_NRC/OpenMAPs/HPC_Job/A' #'transfer'