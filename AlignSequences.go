// This program invokes muscle to align sequences of the same roary clusters.
// Created by Mingzhi Lin (mingzhi9@gmail.com).
package main

import (
	"bytes"
	"database/sql"
	"fmt"
	"io"
	"os"
	"os/exec"
	"runtime"

	"github.com/cheggaaa/pb"
	_ "github.com/mattn/go-sqlite3"
	"github.com/kussell-lab/biogo/seq"
	"gopkg.in/alecthomas/kingpin.v2"
)

func main() {
	var dbFile = kingpin.Arg("db", "sqlite3 db file").Required().String()
	var outFile = kingpin.Arg("out", "output file in csv format").Required().String()
	var ncpu = kingpin.Flag("ncpu", "number of CPUs").Default("0").Int()
	kingpin.Parse()
	if *ncpu == 0 {
		*ncpu = runtime.NumCPU()
	}
	runtime.GOMAXPROCS(*ncpu)
	// open sqilte db.
	db, err := sql.Open("sqlite3", *dbFile)
	checkErr(err)
	defer db.Close()
	// read cluster names.
	clusters := queryClusters(db)
	jobChan := make(chan SeqSet, *ncpu)
	go func() {
		defer close(jobChan)
		seqsChan := readSeqs(db, clusters)
		bar := pb.StartNew(len(clusters))
		for seqs := range seqsChan {
			jobChan <- seqs
			bar.Increment()
		}
		bar.Finish()
	}()
	resChan := make(chan SeqSet, *ncpu)
	done := make(chan bool)
	for i := 0; i < *ncpu; i++ {
		go func() {
			for ss := range jobChan {
				if len(ss.FAAs) >= 2 {
					faas, fnas := align(ss.FAAs, ss.FNAs)
					resChan <- SeqSet{Cluster: ss.Cluster, FAAs: faas, FNAs: fnas}
				}
			}
			done <- true
		}()
	}
	go func() {
		defer close(resChan)
		for i := 0; i < *ncpu; i++ {
			<-done
		}
	}()
	recordChan := make(chan SeqRecord)
	go func() {
		defer close(recordChan)
		for res := range resChan {
			for _, s := range res.FNAs {
				recordChan <- s
			}
			for _, s := range res.FAAs {
				recordChan <- s
			}
		}
	}()
	write(*outFile, recordChan)
}

// SeqSet contains sets of sequences.
type SeqSet struct {
	Cluster    string
	FAAs, FNAs []SeqRecord
}

func align(faas, fnas []SeqRecord) (faaAlns, fnaAlns []SeqRecord) {
	faaAlns = MultiAlign(faas, muscle)
	fnaMap := make(map[string]SeqRecord)
	for _, s := range fnas {
		fnaMap[s.SeqID] = s
	}
	for i := range faaAlns {
		faa := faaAlns[i]
		aa := faa.Seq
		na := fnaMap[faa.SeqID]
		aln := BackTranslate(aa, na.Seq)
		if len(aln)/3 == len(aa) {
			fnaAlns = append(fnaAlns, SeqRecord{SeqID: na.SeqID, SeqType: na.SeqType, Seq: aln, Genome: na.Genome, Cluster: na.Cluster})
		}
		faa.Genome = na.Genome
		faa.Cluster = na.Cluster
		faaAlns[i] = faa
	}
	return
}

// BackTranslate back translates amino acid alignment to nucleotide sequences.
func BackTranslate(aa, na string) string {
	k := 0
	aln := []byte{}
	for i := 0; i < len(aa); i++ {
		if aa[i] == '-' {
			aln = append(aln, []byte{'-', '-', '-'}...)
		} else {
			if (k+1)*3 > len(na) {
				return ""
			}
			aln = append(aln, na[k*3:(k+1)*3]...)
			k++
		}
	}
	return string(aln)
}

// MultiAlignFunc is a interface for multiple alignment function.
type MultiAlignFunc func(stdin io.Reader, stdout, stderr io.Writer, options ...string) error

// MultiAlign aligns sequence alignment of protein sequences
// and back translate them to nucleotide sequences
func MultiAlign(seqRecords []SeqRecord, alignFunc MultiAlignFunc, options ...string) []SeqRecord {
	// prepare protein sequences in fasta format
	stdin := new(bytes.Buffer)
	for _, sr := range seqRecords {
		stdin.WriteString(">" + sr.SeqID + "\n")
		stdin.WriteString(string(sr.Seq) + "\n")
	}
	stdout := new(bytes.Buffer)
	stderr := new(bytes.Buffer)
	alignFunc(stdin, stdout, stderr, options...)
	fr := seq.NewFastaReader(stdout)
	alns, err := fr.ReadAll()
	if err != nil {
		panic(string(stderr.Bytes()))
	}

	var alnRecords []SeqRecord
	for _, s := range alns {
		alnRecords = append(alnRecords, SeqRecord{SeqID: s.Id, Seq: string(s.Seq)})
	}
	return alnRecords
}

// do multiple sequence alignment using muscle
func muscle(stdin io.Reader, stdout, stderr io.Writer, options ...string) (err error) {
	cmd := exec.Command("muscle", options...)
	cmd.Stdin = stdin
	cmd.Stdout = stdout
	cmd.Stderr = stderr
	err = cmd.Run()
	return
}

// SeqRecord contains a record for a sequence.
type SeqRecord struct {
	Cluster, Genome, SeqID, SeqType, Seq string
}

func write(file string, c chan SeqRecord) {
	w, err := os.Create(file)
	checkErr(err)
	defer w.Close()
	buffer := bytes.NewBufferString("")
	size := 5000
	k := 0
	for sr := range c {
		if k > size {
			w.WriteString(buffer.String())
			k = 0
			buffer = bytes.NewBufferString("")
		}
		line := fmt.Sprintf("%s,%s,%s,%s,%s\n", sr.Cluster, sr.SeqID, sr.SeqType, sr.Seq, sr.Genome)
		buffer.WriteString(line)
		k++
	}
	w.WriteString(buffer.String())
}

// readSeqs returns a cluster of sequences.
func readSeqs(db *sql.DB, clusters []string) (c chan SeqSet) {
	c = make(chan SeqSet)
	go func() {
		defer close(c)
		for _, cluster := range clusters {
			stmp, err := db.Prepare("select sequence.seqid, sequence.seq, sequence.seqtype, sequence.genome from cluster, sequence where cluster = ? and cluster.seqid = sequence.seqid")
			checkErr(err)
			defer stmp.Close()
			rows, err := stmp.Query(cluster)
			checkErr(err)
			defer rows.Close()
			seqs := SeqSet{Cluster: cluster}
			var seqID, seqStr, seqType, genome string
			for rows.Next() {
				err := rows.Scan(&seqID, &seqStr, &seqType, &genome)
				checkErr(err)
				s := SeqRecord{Cluster: cluster, SeqID: seqID, SeqType: seqType, Genome: genome, Seq: seqStr}
				if seqType == "prot" {
					seqs.FAAs = append(seqs.FAAs, s)
				} else if seqType == "nucl" {
					seqs.FNAs = append(seqs.FNAs, s)
				}
			}
			c <- seqs
		}
	}()
	return
}

// queryClusters read all cluster names from a dbfile.
func queryClusters(db *sql.DB) (clusters []string) {
	stmt, err := db.Prepare("select cluster, count(*) from cluster group by cluster")
	checkErr(err)
	defer stmt.Close()
	rows, err := stmt.Query()
	checkErr(err)
	defer rows.Close()
	var cluster string
	var count int
	for rows.Next() {
		err := rows.Scan(&cluster, &count)
		checkErr(err)
		if count >= 2 {
			clusters = append(clusters, cluster)
		}
	}
	return
}

// checkErr check error and panic if not nil.
func checkErr(err error) {
	if err != nil {
		panic(err)
	}
}
