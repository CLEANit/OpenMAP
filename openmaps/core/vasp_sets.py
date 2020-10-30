from pymatgen.io.vasp.inputs import Kpoints
from pymatgen.io.vasp.inputs import Incar


def incar_RelaxSet():
    incar_RelaxSet = {
        # General Setup
        "PREC": 'Accurate',  # Options: Normal, Medium, High, Low
        "ENCUT": 520,  # Kinetic Energy Cutoff in eV # max(ENMAX)x1.3
        "ISTART": 0,  # Job: 0-new  1-cont  2-samecut
        "ICHARG": 2,  # initial charge density: 1-file 2-atom 10-cons 11-DOS
        "ISPIN": 1,  # Spin Polarize: 1-No 2-Yes
        # Electronic Relaxation (SCF)
        "NELM": 60,  # Max Number of Elec Self Cons Steps
        "NELMIN": 2,  # Min Number of ESC steps
        "NELMDL": 10,  # Number of non-SC at the beginning
        "EDIFF": 1.0E-05,  # Stopping criteria for ESC
        "LREAL": 'False',  # Real space projection
        "IALGO": 48,  # Electronic algorithm minimization
        "VOSKOWN": 1,  # 1- uses VWN exact correlation
        "ADDGRID": 'True',  # Improve the grid accuracy
        # Ionic Relaxation
        "EDIFFG": -1.0E-04,  # Stopping criteria for ionic self cons steps
        "NSW": 99,  # Max Number of ISC steps: 0- Single Point
        "IBRION": 2,  # Ionic Relaxation Method: 0-MD 1-qNewton-RaphsonElectronic 2-CG
        "ISIF": 3,  # Stress and Relaxation: 2-Ion 3-cell+ion
        "ADDGRID": 'True',  # Improve the grid accuracy
        "SIGMA": 0.05,  # Insulators/semiconductors=0.1  metals=0.05
        "ISMEAR": 1,  # Partial Occupancies for each Orbital # -5 DOS, -2 from file, -1 Fermi Smear, 0 Gaussian Smear
        # Parallelization
        # "NPAR" : 8
        # "NCORE" : 8
        "LPLANE": 'True',
        "LSCALU": 'False',
        "NSIM": 4
    }
    return incar_RelaxSet


class RelaxSet(object):
    def __init__(self, incar=Incar(incar_RelaxSet()), kpoint=None):
        self.incar = incar
        self.kpoint = kpoint
