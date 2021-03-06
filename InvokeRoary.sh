# This script uses roary to create pan genome.
# Created by Mingzhi Lin (mingzhi9@gmail.com).
# Usage:
# bash InvokeRoary.sh <accession list file> <prokka folder> <roary folder>
# It requires
# (1) https://github.com/sanger-pathogens/Roary
# (2) https://www.gnu.org/software/parallel
# If you are using NYU HPC, ask hpc@nyu.edu for help.

accession_list=${1}
prokka_dir=${2}
roary_dir=${3}
roary_gff_dir=${roary_dir}_gffs
if [[ -d ${roary_dir} ]]; then
    rm -r ${roary_dir}
fi
if [[ -d ${roary_gff_dir} ]]; then
    rm -r ${roary_gff_dir}
fi
mkdir ${roary_gff_dir}

function copy_gff_file() {
    genome=$1
    prokka_dir=$2
    roary_dir=$3
    cp ${prokka_dir}/${genome}/${genome}.gff ${roary_dir}
}
export -f copy_gff_file
parallel copy_gff_file {} ${prokka_dir} ${roary_gff_dir} :::: ${accession_list}

ncpu=`nproc`
echo "Running Roary in quiet mode"
logfile="roary.log"
roary -v -p $ncpu -f ${roary_dir} ${roary_gff_dir}/*.gff &> $logfile
mv $logfile ${roary_dir}
echo "Completed running Roary, see log file in ${roary_dir}/roary.log"
