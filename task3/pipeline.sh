fastqc ERR15404843.fastq.gz

bwa index GCF_000005845.2_ASM584v2_genomic.fna

bwa mem -t 10 GCF_000005845.2_ASM584v2_genomic.fna ERR15404843.fastq.gz > out.sam

samtools view -bS out.sam > out.bam

samtools flagstat out.bam | python3 script.py

samtools sort out.bam > out.sorted.bam

freebayes -f GCF_000005845.2_ASM584v2_genomic.fna out.sorted.bam > freebayes_report.vcf
