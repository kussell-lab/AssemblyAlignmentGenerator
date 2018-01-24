"""
This script loads sequences and clusters into a sqlitedb.
Created by Mingzhi Lin (mingzhi9@gmail.com).
"""
import sys
import os
import sqlite3
from Bio import SeqIO
from tqdm import tqdm

def read_accession_list(accession_file):
    """read the list of accession in the file"""
    accession_list = []
    with open(accession_file, 'r') as reader:
        for line in reader:
            accession_list.append(line.rstrip())
    return accession_list

def read_fasta(fasta_file):
    """read sequences from a fasta file"""
    records = []
    with open(fasta_file, 'r') as input:
        file_format = "fasta"
        for seq_rec in SeqIO.parse(input, file_format):
            records.append((seq_rec.id, str(seq_rec.seq)))
    return records

def read_roary(roary_cluster_file):
    """read roary output cluster file"""
    records = []
    with open(roary_cluster_file, 'rU') as handle:
        for line in handle:
            line = line.rstrip()
            clst = line.split(': ')[0]
            terms = line.split(': ')[1].split('\t')
            for term in terms:
                records.append((clst, term))
    return records 

def read_seq_from_genome(accession, genome_dir):
    """read protein and nucleotide sequences of a genome"""
    protein_file = os.path.join(genome_dir, accession, accession + ".faa")
    protein_records = read_fasta(protein_file)
    nucleotide_file = os.path.join(genome_dir, accession, accession + ".ffn")
    nucleotide_records = read_fasta(nucleotide_file)
    records = []
    for rec in protein_records:
        records.append((accession, rec[0], "prot", rec[1]))
    for rec in nucleotide_records:
        records.append((accession, rec[0], "nucl", rec[1]))
    return records

def create_sequence_table(conn):
    """create sequence table in sqlite"""
    cur = conn.cursor()
    sql = "drop table if exists sequence"
    cur.execute(sql)
    sql = '''CREATE TABLE sequence(
        genome VARCHAR(255),         
        seqid VARCHAR(255),         
        seqtype VARCHAR(255),         
        seq TEXT)'''
    cur.execute(sql)

def create_cluster_table(conn):
    """create sequence cluster table in sqlite"""
    cur = conn.cursor()
    sql = 'drop table if exists cluster'
    cur.execute(sql)
    sql = 'create table cluster(cluster varchar(255), seqid varchar(255))'
    cur.execute(sql)
 
def load_sequences_to_sqlite(conn, records):
    """load sequence records into sqlite"""
    cur = conn.cursor()
    cur.executemany('insert into sequence values(?,?,?,?)', records)
    conn.commit()

def load_clusters_to_sqlite(conn, records):
    """load cluster records into sqlite"""
    cur = conn.cursor()
    cur.executemany('insert into cluster values(?,?)', records)
    conn.commit()
 
def create_sqlite_indices(conn):
    """create sqlite indices"""
    cur = conn.cursor()
    sql = "create index idx_seq_genome on sequence(genome)"
    cur.execute(sql)
    sql = "create index idx_seqid on sequence(seqid)"
    cur.execute(sql)
    sql = "create index idx_seqtype on sequence(seqtype)"
    cur.execute(sql)
    conn.commit()

def main():
    """main function"""
    accession_list_file = sys.argv[1]
    prokka_dir = sys.argv[2]
    roary_dir = sys.argv[3]
    sqlite_file = sys.argv[4]
    
    conn = sqlite3.connect(sqlite_file)

    print("Loading sequences into sql database...")
    create_sequence_table(conn)
    accession_list = read_accession_list(accession_list_file)
    for accession in tqdm(accession_list):
        records = read_seq_from_genome(accession, prokka_dir)
        load_sequences_to_sqlite(conn, records)

    print("Loading roary cluster results into sql database...")
    create_cluster_table(conn)
    roary_cluster_file = os.path.join(roary_dir, "clustered_proteins")
    cluster_records = read_roary(roary_cluster_file)
    load_clusters_to_sqlite(conn, cluster_records)
    print("Total %d clusters" % len(cluster_records))

    create_sqlite_indices(conn)
    conn.close()
if __name__ == "__main__":
    main()
