
import os

job_types = ['DOS', 'BS', 'Static', 'Relaxation']


def job_descriptor(nb_atoms, job_type):
    """
    :param nb_atoms: number of atoms in the system (int)
    :param job_type: Type of calculation ( energy, relaxation, bandgap)
    :return: dictionary with job parameter
    """
    job_description = {}

    # time, n_cpu, n_gpu,

    return job_description


def write_slurm_from_file(input_path, file):
    """
    :param input_path: path to write the slurm job file
    :param file: template slurm job file
    :return:
    """

    ifile = open(file, 'r')
    script = ifile.readlines()
    ifile.close()
    if not os.path.isdir(input_path):
        raise Exception('The directory {} does not exist'.format(input_path))

    basename = os.path.basename(os.path.normpath(input_path))

    outputfile = os.path.join(input_path, basename + '_vasp_job.sh')

    jobname = basename
    for line in script:
        if '#SBATCH --job-name=' in line:
            line.replace('job_name', jobname)
    ofile = open(outputfile, 'w')
    ofile.write(script)
    ofile.close()


def write_slurm_job(input_path, job_description, gpu=0):
    """ "
    inputfiles_path : path to write the slurm job file
    job_description : dictionary with the parameters of the job
    gpu : boolean, gpu or not
    """
    # for path_dir in
    # glob.glob(os.path.join(inputfiles_path,'{}s*/'.format(project_name):
    if not os.path.isdir(input_path):
        raise Exception('The directory {} does not exist'.format(input_path))

    basename = os.path.basename(os.path.normpath(input_path))

    outputfile = os.path.join(input_path, basename + '_vasp_job.sh')

    vm_file = os.path.join(basename + '_vm.py')

    jobname = basename

    script = '#!/bin/bash\n'
    script += '#SBATCH --account={}\n'.format(job_description['account'])
    script += '#SBATCH --job-name={}\n'.format(jobname)
    script += '#SBATCH --time={0}-00:00:00 #d-hh:mm:ss\n'.format(
        job_description['time'])
    script += '#SBATCH --output=%x-%j.out\n'
    script += '#SBATCH --error=%x-%j.err\n'

    if int(gpu) > 0:
        script += '#SBATCH --cpus-per-task={0} # number of CPU processes\n'.format(
            job_description['ntask'])
        script += '#SBATCH --gres=gpu:{0} # Number of GPUs (per node) \n'.format(
            job_description['gpu'])
        script += '#SBATCH --mem = {0}M #  memory (per node)\n'.format(
            job_description['memory'])
    else:
        script += '#SBATCH --ntasks={0} # number of MPI processes\n'.format(
            job_description['ntask'])
        script += '#SBATCH --mem-per-cpu={0}M # megabytes\n'.format(
            job_description['memory'])

    if job_description['email'] is not None:
        script += '#SBATCH --mail-user={0}\n'.format(job_description['email'])
        script += '#SBATCH --mail-type=ALL\n'

    script += '\n\n'
    ######################################
    # Section for defining job variables and settings:

    # When you use this test script, make sure, your folder structure is as follows:
    # ./job_vasp.sh
    # ./vasp_input/INCAR
    # ./vasp_input/KPOINTS
    # ./vasp_input/POTCAR
    # ./vasp_input/POSCAR

    script += 'export proj={} # Name of job folder\n'.format('vasp_input')
    script += 'tar xvf {}.tar\n'.format('vasp_input')
    script += 'input=$(ls ${proj}/{INCAR,KPOINTS,POTCAR,POSCAR})  # Input files from job folder\n'
    script += '\n\n'
    # We load all the default program system settings with module load:
    script += 'module --quiet purge\n'
    script += 'module load intel/2018.3  intelmpi/2018.3\n'
    script += (
        'export  LD_LIBRARY_PATH=/opt/software/intel/mkl/lib/intel64_lin/:/opt/software/intel'
        '/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/:/opt/software/gcc-6.4.0/lib64/\n '
    )
    # script += "module load vasp/6.1\n"

    # Now we create working directory and temporary scratch for the job(s):
    script += '\n\n'
    script += 'export VASP_WORKDIR=$SCRATCH/$SLURM_JOB_ID\n'
    script += 'mkdir -p $VASP_WORKDIR\n'

    # Preparing and moving inputfiles to tmp:
    script += 'cp $input $VASP_WORKDIR\n'
    script += 'cd $VASP_WORKDIR\n'

    ######################################
    # Section for running the program and cleaning up:

    # Running the program:

    if gpu:
        script += 'mpiexec <VASP>\n'
    else:
        script += 'time srun {}\n'.format(job_description['binary'])

    script += '\n\n'

    script += 'out=$(ls {OUTCAR,XDATCAR,OSZICAR,CONTCAR,DOSCAR,CHGCAR,vasprun.xml})' '# Input files from job folder\n'
    script += ' mkdir -p vasp_output\n'

    script += 'cp * vasp_output\n'
    script += 'cp -r vasp_output/  $SLURM_SUBMIT_DIR\n'
    script += 'cd  $SLURM_SUBMIT_DIR\n'
    # script += "mv *.err *.out  vasp_output\n"
    script += 'rm -r $VASP_WORKDIR\n'
    script += '\n\n'
    # script += 'source ~/ENV_PYTHON/bin/activate\n'
    # script += 'python ~/OpenMAP/objective.py  {} \n'.format(
    #     job_description['objective_name'])
    # script += 'python  ./{}\n'.format(vm_file)

    script += '\n\n'
    script += 'echo exit 0'
    ofile = open(outputfile, 'w')
    ofile.write(script)
    ofile.close()
