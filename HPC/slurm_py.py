#!/usr/bin/env python
from optparse import OptionParser
import os
import os.path
import subprocess
import re


class Partition(object):

    def __init__(self, name, maxDays):
        self.name = name
        self.maxDays = maxDays


usage = "usage: %prog [options] inputfiles"
parser = OptionParser(usage=usage)

parser.add_option("-n", "--name", dest="name",
                  help="Name of the job. Default: name of the inputfile",
                  action="store", type="string", default="")

parser.add_option("-m", "--memory", dest="memory",
                  help="RAM Memory in MB. Default: 1024",
                  action="store", type="string", default="1024")

parser.add_option("-t", "--time", dest="time",
                  help="Time in days. Default: 1",
                  action="store", type="string", default="1")

parser.add_option("-p", "--processors", dest="processors",
                  help="Number of processors. Default: 1",
                  action="store", type="string", default="1")

parser.add_option("-e", "--exclude", dest="exclude",
                  help="Exclude a list of node (separated by comma).",
                  action="store", type="string", default="dr20")

parser.add_option("-r", "--run", dest="run",
                  help="Submit the job. Default: False (only create the sbatch script)",
                  action="store_true", default=False)

(options, args) = parser.parse_args()

inputfiles = args
if len(inputfiles) == 0:
    parser.error("No input log file given")

# Memory
try:
    memory = int(options.memory)
except ValueError:
    parser.error("Cannot convert memory option into integer")
if memory <= 0:
    parser.error("Memory option should be larger than zero")
# time
try:
    time = int(options.time)
except ValueError:
    parser.error("Cannot convert time option into integer")
if time <= 0:
    parser.error("Time option should be larger than zero")
# processors
try:
    processors = int(options.processors)
except ValueError:
    parser.error("Cannot convert processors option into integer")
if processors <= 0:
    parser.error("Processors option should be larger than zero")

# exclude
excludeNodes = None if len(options.exclude.strip()) == 0 else options.exclude

# email
email = os.environ.get("ISCF_EMAIL")

# create list of partition using sinfo -o "%R %l"
pattern = r"%d+"
p = subprocess.Popen(['sinfo', '-o', '%R %l'], stdout=subprocess.PIPE)
info = p.stdout.readlines()[1:]
partitions = []
for line in info:
    if len(line.strip()) == 0:
        continue
    partition_name = line.split()[0]
    if "gpu" in partition_name:
        continue
    partition_time = int(re.findall(r"\d+", line)[0])
    partitions.append(Partition(partition_name, partition_time))

partition = None
for part in partitions:
    if time <= part.maxDays:
        partition = part
        break
if partition is None:
    parser.error("The time exceed the maximum time limit: {} days".format(partitions[-1].maxDays))

for inputfile in inputfiles:
    if not os.path.isfile(inputfile):
        print("The file ['%s'] does not exist" % inputfile)
        continue
    basename, ext = os.path.splitext(inputfile)
    if ext != ".com":
        print("The file ['%s'] is not a Gaussian com file" % inputfile)
        continue
    outputfile = basename + ".sbatch"
    # jobname
    jobname = options.name if len(options.name) > 0 else basename

    script = "#!/bin/bash\n"
    script += "#SBATCH --job-name={0}\n".format(jobname)
    script += "#SBATCH --time={0}-00:00:00 #d-hh:mm:ss\n".format(time)
    script += "#SBATCH --ntasks={0}\n".format(1)
    script += "#SBATCH --cpus-per-task={0}\n".format(processors)
    script += "#SBATCH --mem-per-cpu={0} # megabytes\n".format(memory)
    script += "#SBATCH --partition={0}\n".format(partition.name)
    if excludeNodes is not None:
        script += "#SBATCH --exclude=\"{0}\"\n".format(excludeNodes)

    if email is not None:
        script += "#SBATCH --mail-user={0}\n".format(email)
        script += "#SBATCH --mail-type=ALL\n"

    script += "echo \"Node: $(hostname)\"\n"
    script += "export input={0}\n".format(basename)
    script += "module load gaussian/09_D01\n"
    script += "WORKDIR=\"$LOCALSCRATCH/$SLURM_JOB_ID\"\n"
    script += "export GAUSS_SCRDIR=$WORKDIR\n"
    script += "mkdir -p $WORKDIR\n"
    # script += "cp \"$SLURM_SUBMIT_DIR/$input.com\" $WORKDIR\n"
    # script += "cd $WORKDIR\n"
    script += "g09 < \"$input.com\" > \"$SLURM_SUBMIT_DIR/$input.log\"\n"
    # script += "cp \"$WORKDIR\"/*.chk \"$SLURM_SUBMIT_DIR/\"\n"
    script += "rm -rf $WORKDIR\n"
    script += "\n\n"

    ofile = open(outputfile, "w")
    ofile.write(script)
    ofile.close()

    if options.run:
        subprocess.call(["sbatch", outputfile])
