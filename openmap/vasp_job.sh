#!/bin/bash
#SBATCH --account=def-itamblyn-ac
#SBATCH --job-name=job_name
#SBATCH --time=1-00:00:00 #d-hh:mm:ss
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --ntasks=4 # number of MPI processes
#SBATCH --mem-per-cpu=4000M # megabytes


export proj=vasp_input # Name of job folder




input=$(ls ${proj}/{INCAR,KPOINTS,POTCAR,POSCAR})  # Input files from job folder


module --quiet purge
module load intel/2018.3  intelmpi/2018.3
export  LD_LIBRARY_PATH=/opt/software/intel/mkl/lib/intel64_lin/:/opt/software/intel/compilers_and_libraries_2018.3.222/linux/mpi/intel64/lib/:/opt/software/gcc-6.4.0/lib64/


export VASP_WORKDIR=$SCRATCH/$SLURM_JOB_ID
mkdir -p $VASP_WORKDIR
cp $input $VASP_WORKDIR
cd $VASP_WORKDIR

totT=0
for a in `seq -w 3.5 0.1 4.5`
do
  echo "a=$a"
  sed
cp INCAR.vol INCAR
cp KPOINTS.vol KPOINTS

time mpirun -np 8 $HOME/bin/vasp/vasp_std
time srun $HOME/bin/vasp/vasp_std
V=`grep volume/ion OUTCAR|awk  ' {print $5}'`
E=`tail -n1  OSZICAR | awk '{ print $5/4}'`
totT=`echo $totT $T | awk '{print $1+$2}'`
echo $V $E >> EvsV
echo $a $E >> EvsA

./cleanvaspfiles
rm -f CHG* CONTCAR* DOSCAR* DYNMAT EIGENVAL IBZKPT OPTIC OSZICAR* OUTCAR* PROCAR* \
      PCDAT W* XDATCAR* PARCHG* vasprun.xml SUMMARY.* REPORT


done

out=$(ls {OUTCAR,XDATCAR,OSZICAR,CONTCAR,DOSCAR,CHGCAR,vasprun.xml})# Input files from job folder
mkdir -p vasp_output
cp * vasp_output
cp -r vasp_output  $SLURM_SUBMIT_DIR
cd  $SLURM_SUBMIT_DIR
mv *.err *.out  vasp_output
rm -r $VASP_WORKDIR


