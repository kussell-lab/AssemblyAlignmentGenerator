"""
This script extracts core gene sets.
Created by Mingzhi Lin (mingzhi9@gmail.com).
"""
import sys
from tqdm import tqdm

def read_accession_list(accession_file):
    """read a list of accessions from a file"""
    accession_list = []
    with open(accession_file) as reader:
        for line in reader:
            term = line.rstrip()
            accession_list.append(term)
    return accession_list

def read_alignments(alignment_file):
    """read clusters of alignment"""
    clusters = {}
    with open(alignment_file) as infile:
        for line in infile:
            terms = line.rstrip().split(',')
            cluster, seqid, seqtype, seq = terms[0], terms[1], terms[2], terms[3]
            if seqtype == 'nucl':
                if cluster not in clusters:
                    clusters[cluster] = []
                clusters[cluster].append((seqid, seq))
    return clusters

def split_cluster(cluster, sequences):
    """Split cluster"""
    profile_dict = {}
    for (seqid, seq) in sequences:
        profile = ""
        for nuclacid in seq:
            if nuclacid == '-':
                profile = profile + "1"
            else:
                profile = profile + "0"
        if profile not in profile_dict:
            profile_dict[profile] = []
        profile_dict[profile].append((seqid, seq))
    clusters = []
    index = 0
    for seqs in profile_dict.values():
        for (i, (seqid, seq)) in enumerate(seqs):
            seq = seq.replace('-', '')
            clst = "%s_%d" % (cluster, index)
            seqid = clst + "|" + seqid
            seqs[i] = (seqid, seq)
        index = index + 1
        clusters.append(seqs)
    return clusters

def write(writer, clusters):
    """write clusters"""
    for sequences in clusters:
        for (seqid, seq) in sequences:
            writer.write('>' + seqid + '\n')
            writer.write(seq + '\n')
        writer.write('=\n')

def main():
    """extract core and flex gene sets"""
    accession_list_file = sys.argv[1]
    alignment_file = sys.argv[2]
    output_file = sys.argv[3]
    num_genomes = len(read_accession_list(accession_list_file))
    alignment_clusters = read_alignments(alignment_file)
    
    print("Extract core genes...")
    writer = open(output_file, 'w')
    count = 0
    for cluster, sequences in tqdm(alignment_clusters.items()):
        if len(sequences) == num_genomes:
            clusters = split_cluster(cluster, sequences)
            write(writer, clusters)
            count = count + 1
    writer.close()
    print("Total %d core gene alignments extracted, which were saved to %s" % (count, output_file))

if __name__ == "__main__":
    main()
