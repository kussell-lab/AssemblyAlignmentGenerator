FROM ubuntu:17.10

RUN apt-get update
RUN apt-get install -y golang python-pip git muscle roary parallel libdatetime-perl libxml-simple-perl libdigest-md5-perl git default-jre bioperl

RUN pip install --upgrade pip
RUN pip install tqdm biopython

RUN go get -u github.com/cheggaaa/pb
RUN go get -u github.com/mattn/go-sqlite3
RUN go get -u gopkg.in/alecthomas/kingpin.v2
RUN go get -u github.com/kussell-lab/biogo/seq

RUN git clone https://github.com/tseemann/prokka.git /opt/prokka
RUN git clone https://github.com/kussell-lab/AssemblyAlignmentGenerator /opt/AssemblyAlignmentGenerator
ENV PATH="/opt/prokka/bin:/opt/AssemblyAlignmentGenerator:${PATH}"

RUN /bin/bash -c "prokka --setupdb"
RUN /bin/bash -c "echo 'will cite' | parallel --citation"
