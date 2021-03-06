# This script uses prokka to re-annotate genomes.
# Create by Mingzhi Lin (mingzhi9@gmail.com).
# Usage:
# bash InvokeProkka.sh <accession list file> <genome folder> <prokka output folder>
# It requires
# (1) https://github.com/tseemann/prokka
# (2) https://www.gnu.org/software/parallel
# If you are using NYU HPC, ask hpc@nyu.edu for help.

function invoke_prokka() {
    genome=$1
    workspace=$2
    genomefile=$3/$genome/${genome}_genomic.fna
    prokka --cpus 1 --force --centre X --compliant --outdir ${workspace}/${genome} --prefix ${genome} ${genomefile} --quiet
}
export -f invoke_prokka

accessionlistfile=$1
genomefolder=$2
prokkafolder=$3
echo "Inovking Prokka to re-annotate genomes..."
parallel invoke_prokka {} $prokkafolder $genomefolder :::: $accessionlistfile
echo "Completed running Prokka, saved results to ${prokkafolder}"
