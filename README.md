# AssemblyAlignmentGenerator
Generating core-gene alignments from a list of assemblies.

## Installation
These scripts were written in Bash, Go and Python3. It require following programs:
* [Parallel](https://www.gnu.org/software/parallel/);
* [Prokka](https://github.com/tseemann/prokka);
* [Roary](https://github.com/sanger-pathogens/Roary);
* [Muscle](https://www.drive5.com/muscle);

and Python3 libaries:
* `pip3 install --user tqdm`

and Go libaries:
* `go get -u github.com/cheggaaa/pb`
* `go get -u github.com/mattn/go-sqlite3`
* `go get -u gopkg.in/alecthomas/kingpin.v2`

## Usage
`bash RunAll.sh <assembly summary file> <accession list file> <output directory> <output prefix>`
  * `<assembly summary file>` can be downloaded from [here](ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt);
  * `<accession list file>` contain a list of assembly accessions;
  * `<output directory>` contains the results;
  * `<output prefix>` is the prefix of the results.
