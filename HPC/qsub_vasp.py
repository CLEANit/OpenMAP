import os


def write_vasp_slurm_job(inputfiles_path, job_description, gpu=False):
    """"
    inputfiles_path : path to directory with the input files
    job_description : dictionary with the parameters of the job
    gpu : boolean, gpu or not
    """
    # for path_dir in glob.glob(os.path.join(inputfiles_path,'{}s*/'.format(project_name):
    if not os.path.isdir(inputfiles_path):
        raise Exception("The directory {} does not exist".format(inputfiles_path))
        # print("The directory {} does not exist".format(inputfiles_path))
        # continue
    # path = pathlib.PurePath(inputfiles_path)
    # basename = path.name

    basename = os.path.basename(os.path.normpath(inputfiles_path))

    outputfile = os.path.join(inputfiles_path, basename + "_vasp_job.sh")
    # jobname
    jobname = basename

    script = "#!/bin/bash\n"
    script += "#SBATCH --account={}\n".format(job_description["account"])
    script += "#SBATCH --job-name={}\n".format(jobname)
    script += "#SBATCH --time={0}-00:00:00 #d-hh:mm:ss\n".format(job_description["time"])
    script += "#SBATCH --output=%x-%j.out.log\n"
    script += "#SBATCH --error==%x-%j.err\n"

    if gpu:
        script += "#SBATCH --cpus-per-task={0} # number of CPU processes\n".format(job_description["ntask"])
        script += "#SBATCH --gres=gpu:{0} # Number of GPUs (per node) \n".format(job_description["gpu"])
        script += "#SBATCH --mem = {0}M #  memory (per node)\n".format(job_description["memory"])
    else:
        script += "#SBATCH --ntasks={0} # number of MPI processes\n".format(job_description["ntask"])
        script += "#SBATCH --mem-per-cpu={0}M # megabytes\n".format(job_description["memory"])

    if job_description['email'] is not None:
        script += "#SBATCH --mail-user={0}\n".format(job_description["email"])
        script += "#SBATCH --mail-type=ALL\n"

    script += "\n\n"
    ######################################
    # Section for defining job variables and settings:

    # When you use this test script, make sure, your folder structure is as follows:
    # ./job_vasp.sh
    # ./vasp_input/INCAR
    # ./vasp_input/KPOINTS
    # ./vasp_input/POTCAR
    # ./vasp_input/POSCAR

    script += "export proj={} # Name of job folder\n".format('job')
    script += "input=$(ls ${proj}/{INCAR, KPOINTS, POTCAR, POSCAR})  # Input files from job folder\n"
    script += "\n\n"
    # We load all the default program system settings with module load:
    script += "module --quiet purge\n"
    script += "module load intel/2018.3  intelmpi/2018.3\n"
    script += "export  LD_LIBRARY_PATH=/opt/software/intel/mkl/lib/intel64_lin/:/opt/software/intel" \
              "/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/:/opt/software/gcc-6.4.0/lib64/\n "
    # script += "module load vasp/6.1\n"

    # Now we create working directory and temporary scratch for the job(s):
    script += "\n\n"
    script += "export VASP_WORKDIR=$SCRATCH/$SLURM_JOB_ID\n"
    script += "mkdir -p $VASP_WORKDIR\n"

    # Preparing and moving inputfiles to tmp:
    script += "cp $input $VASP_WORKDIR\n"
    script += "cd VASP_WORKDIR\n"

    ######################################
    # Section for running the program and cleaning up:

    # Running the program:

    if gpu:
        script += "mpiexec <VASP>\n"
    else:
        script += "srun $HOME/bin/vasp/vasp_std\n"


    script += "\n\n"

    script += "output=$(ls ${VASP_WORKDIR}/{OUTCAR, XDATCAR, OSZICAR, CONTCAR, DOSCAR, CHGCAR,vasp.out,vasprun.xml}) " \
              " # Input files from job folder\n "

    script += "cp $output  $SLURM_SUBMIT_DIR/${proj}\n"

    # script += "    cp OUTCAR $SLURM_SUBMIT_DIR/${proj}.OUTCAR \n"
    # To zip some of the output might be a good idea!
    # gzip results.gz OUTCAR
    # mv $results.gz $submitdir/

    script += "cd  $SLURM_SUBMIT_DIR\n"
    script += "rm -r $VASP_WORKDIR/*\n"
    script += "\n\n"

    ofile = open(outputfile, "w")
    ofile.write(script)
    ofile.close()
