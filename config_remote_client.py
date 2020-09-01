"""Remote host configuration."""
import os

from dotenv import load_dotenv
import getpass

# Load environment variables from .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Read environment variables
#host = os.environ.get('cedar.computecanada.ca') # ('REMOTE_HOST')
#user = os.environ.get('ctetsass') # ('REMOTE_USERNAME')
#ssh_key_filepath = os.environ.get('~/.ssh') # ('SSH_KEY')
#remote_path = os.environ.get('/home/ctetsass/scratch')# ('REMOTE_PATH')
#passphrase = 'Gastipard_Isaro' # getpass.getpass()

project_name = 'Alloys'
host = 'cedar.computecanada.ca' # ('REMOTE_HOST')
account = 'def-itamblyn-ac'
user = 'ctetsass' # ('REMOTE_USERNAME') getpass.getuser()
ssh_key_filepath = '~/.ssh/id_rsa' # ('SSH_KEY')
#remote_path = '/home/ctetsass/scratch/OpenMaps'+'/'+project_name  # ('REMOTE_PATH')
remote_path = os.path.join('/home/ctetsass/projects/rrg-itamblyn-ab/OpenMaps',project_name)
#passphrase = 'Gastipard_Isaro' # getpass.getpass()
passphrase = None
local_file_directory = os.path.join('/Users/ctetsass/Calculation_NRC/OpenMAPs', 'HPC_Job', project_name) #'transfer'

#data_path = ''