"""
Fetch genome sequences from NCBI FTP.
Create by Mingzhi Lin (mingzhi9@gmail.com).
Inputs:
(1) ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt;
(2) assembly accession list file;
(3) output directory.
Usage:
    python FetchGenomes.py <assembly_summary_refseq.txt> <assembly accession list file> <output directory>
"""
import sys
import gzip
import os
import ftplib
import tqdm

def main():
    """
    main function
    """
    # parse command arguments.
    assembly_summary_file = sys.argv[1]
    assembly_accession_list_file = sys.argv[2]
    out_dir = sys.argv[3]

    # read the list of assembly accessions.
    assembly_accession_set = set()
    with open(assembly_accession_list_file, 'r') as input_file:
        for line in input_file:
            accession = line.rstrip()
            assembly_accession_set.add(accession)

    # read assembly summary report file, which is a TAB file,
    # and obtain a hashmap of accession:ftp path.
    assembly_ftp_paths = {}
    with open(assembly_summary_file, 'r') as input_file:
        header = []
        for line in input_file:
            terms = line.rstrip().split("\t")
            if line.startswith('#'):
                header = terms
            else:
                accession = terms[0]
                ftp_path = terms[header.index("ftp_path")]
                if accession in assembly_accession_set:
                    assembly_ftp_paths[accession] = ftp_path
    
    # download genomic sequences from FTP.
    print("Fetching genome sequences from NCBI FTP:")
    host = "ftp.ncbi.nlm.nih.gov"
    ftp = ftplib.FTP(host, "anonymous", "ml3365@nyu.edu")
    for accession in tqdm.tqdm(assembly_ftp_paths.keys()):
        # create assembly output directory if not exists.
        assembly_out_dir = os.path.join(out_dir, accession)
        if not os.path.exists(assembly_out_dir):
            os.makedirs(assembly_out_dir)

        ftp_path = assembly_ftp_paths[accession].replace('ftp://%s/' % host, "")
        base_name = os.path.basename(assembly_ftp_paths[accession])
        appendix_list = ["_genomic.fna.gz"]
        for appendix in appendix_list:
            # download file from FTP.
            ftp_file_path = os.path.join(ftp_path, base_name + appendix)
            local_gzip_file = os.path.join(assembly_out_dir, accession + appendix)
            with open(local_gzip_file, 'wb') as out:
                ftp.retrbinary('RETR ' + ftp_file_path, out.write)
            # unzip file
            local_text_file = local_gzip_file.replace(".gz", "")
            with open(local_text_file, 'wb') as out:
                with gzip.open(local_gzip_file) as handle:
                    out.write(handle.read())
            os.remove(local_gzip_file)
    print("Genome sequences were saved in %s" % out_dir)

if __name__ == "__main__":
    main()

