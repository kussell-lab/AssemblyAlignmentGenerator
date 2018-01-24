python FetchGenomes.py examples/assembly_summary_refseq.txt examples/TC1_accessions.txt examples/genomes
bash InvokeProkka.sh examples/TC1_accessions.txt examples/genomes examples/prokka
bash InvokeRoary.sh examples/TC1_accessions.txt examples/prokka examples/roary
python LoadSequences.py examples/TC1_accessions.txt examples/prokka examples/roary examples/TC1_sequences.db
go run AlignSequences.go examples/TC1_sequences.db examples/TC1_alignments.csv
python ExtractCoreGenes.py examples/TC1_accessions.txt examples/TC1_alignments.csv examples/TC1_core.xmfa
