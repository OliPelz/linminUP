#PBS -S /bin/bash
#PBS -V 
#PBS -l nodes=1:ppn=6
# #PBS -l mem=4gb
#PBS -o /dev/null
#PBS -e /dev/null

$CMD 2>/dev/null
