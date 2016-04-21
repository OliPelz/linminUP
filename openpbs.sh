#PBS -S /bin/bash
#PBS -V 
#PBS -l nodes=1:ppn=6
# #PBS -l mem=4gb

echo $CMD
$CMD
