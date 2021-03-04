import os

loc = os.path.dirname(os.path.abspath(__file__))
#
with open(os.path.join(loc, 'aws_hpc.txt'), 'r') as fr:
    aws_hcp = fr.readlines()
