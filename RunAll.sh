# This script generates core-gene alignments from a list of assemblies.
# Created by Mingzhi Lin (mingzhi9@gmail.com).
# Usage: bash RunAll.sh <assembly summary file> <accession list> <working direcotry> <prefix>
# Arguments:
#   <assembly summary file> can be download from ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt
#   <accession list file> contains a list of assembly accessions;
#   <working directory> is the working space;
#   <prefix> is the result prefix.
# Results:
#   <working directory>/<prefix>_core.xmfa stores the final alignments of core genomes.

assembly_summary_file=$1
accession_list=$2
working_dir=$3
prefix=$4

if [[ $# -eq 0 ]]; then
    echo "Usage: bash RunAll.sh <assembly summary file> <accession list> <working direcotry> <prefix>"
    exit 1
fi

if [[ ! -d ${working_dir}/genomes ]]; then
    mkdir ${working_dir}/genomes
fi

if [[ ! -d ${working_dir}/prokka ]]; then
    mkdir ${working_dir}/prokka
fi

python3 FetchGenomes.py ${working_dir}/assembly_summary_refseq.txt ${accession_list} ${working_dir}/genomes
bash InvokeProkka.sh ${accession_list} ${working_dir}/genomes ${working_dir}/prokka
bash InvokeRoary.sh ${accession_list} ${working_dir}/prokka ${working_dir}/roary
python3 LoadSequences.py ${accession_list} ${working_dir}/prokka ${working_dir}/roary ${working_dir}/${prefix}_sequences.db
go run AlignSequences.go ${working_dir}/${prefix}_sequences.db ${working_dir}/${prefix}_alignments.csv
python3 ExtractCoreGenes.py ${accession_list} ${working_dir}/${prefix}_alignments.csv ${working_dir}/${prefix}_core.xmfa
