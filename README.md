# AssemblyAlignmentGenerator
This program generates core-gene alignments from a list of assemblies. It downloads the genomic sequences from [ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/](ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/) and re-annotates them using [Prokka](https://github.com/tseemann/prokka). It then uses [Roary](https://github.com/sanger-pathogens/Roary) to generate the [pan-genome](https://en.wikipedia.org/wiki/Pan-genome), and extracts the core genome, which are a set of genes that appear in all the assemblies. The protein sequences of each core gene are aligned by [Muscle](https://www.drive5.com/muscle), and then back-translated to DNA sequences.

## Installation
The program was written in Bash, [Go](https://golang.org) and [Python](https://www.python.org). It requires following programs:
* [Parallel](https://www.gnu.org/software/parallel/);
* [Prokka](https://github.com/tseemann/prokka);
* [Roary](https://github.com/sanger-pathogens/Roary);
* [Muscle](https://www.drive5.com/muscle);

and Python libaries:
* `pip install --user tqdm`

and Go libaries:
* `go get -u github.com/cheggaaa/pb`
* `go get -u github.com/mattn/go-sqlite3`
* `go get -u gopkg.in/alecthomas/kingpin.v2`

## Usage
`AssemblyAlignmentGenerate <assembly summary file> <accession list file> <output directory> <output prefix>`
  * `<assembly summary file>` can be downloaded from [ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt](ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt);
  * `<accession list file>` contain a list of assembly accessions;
  * `<output directory>` contains the results;
  * `<output prefix>` is the prefix of the results.

The output is a XMFA file containing the final alignments of DNA sequences of the core genes. The file can be found in `<output directory>/<output prefix>_core.xmfa`.
