#!/usr/bin/env python
import os
import glob
import pathlib
import sys
import getpass
import paramiko
import re

# if sys.stdin.isatty():
#    p = getpass.getpass('Using getpass: ')
# else:
#    print('Using readline')
#    p = sys.stdin.readline().rstrip()

# print('Read: ', p)

# ================================================
hostname = 'cedar.computecanada.ca'  # sys.argv[1]
account = 'rrg-mkarttu-ab'
username = 'ctetsass'  # sys.argv[2]
password = 'Gastipard_Isaro'  # getpass.getpass()
# ================================================
project_name = 'Alloys'
Work_dir = '$HOME/Calculation_NRC/OpenMAP'
Input_dir = Work_dir + '/Input_HPC/' + project_name
Output_dir = Work_dir + '/Output_HPC/' + project_name


# email =  # os.environ.get("ISCF_EMAIL")
# ================================================


class Partition(object):

    def __init__(self, name, maxDays):
        self.name = name
        self.maxDays = maxDays

def get_partition_info(hostname, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(hostname=hostname, username=username, password=password)

    # create list of partition using sinfo -o "%R %l"
    pattern = r"%d+"

    command = 'sinfo -o "%R %l"'
    _, stdout, stderr = client.exec_command(command)
    info = stdout.readlines()[1:]
    stdout.close()
    stderr.close()
    client.close()

    partitions = []

    for line in info:
        if len(line.strip()) == 0:
            continue
        partition_name = line.split()[0]
        # if "gpu" in partition_name:
        #    continue
        partition_time = int(re.findall(r"\d+", line)[0])
        partitions.append(Partition(partition_name, partition_time))

    return partitions


partitions = get_partition_info(hostname, username, password)




partition = None
for part in partitions:
    if job_description['time'] <= part.maxDays:
        partition = part
        break
if partition is None:
    print(" Running time has been modified to the maximum time limit: {} days".format(partitions[-1].maxDays))
    job_description['time'] = partitions[-1].maxDays

print(partitions[-1].maxDays)





