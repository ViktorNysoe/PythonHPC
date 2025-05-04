#!/bin/bash
#BSUB -J jacobi
#BSUB -o jacobi_output_%J.txt
#BSUB -e jacobi_error_%J.txt
#BSUB -n 8
#BSUB -W 3:00
#BSUB -q gpua100
#BSUB -R "span[hosts=1]"
#BSUB -R "select[gpu32gb] ngpus_excl_p=1"
#BSUB -R "rusage[mem=4GB]"


module load python/3.9.6
python amdahl_dynamic.py 100