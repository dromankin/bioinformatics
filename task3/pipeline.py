import os
import subprocess
import multiprocessing
from toil.common import Toil
from toil.job import Job
from toil.realtimeLogger import RealtimeLogger




SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_fastqc(job, fq_path):
    RealtimeLogger.info(f"Launching fastqc for {fq_path}")
    subprocess.run(f"fastqc {fq_path}", shell=True, check=True)
    return "fastqc_done"

def index_reference(job, ref_fasta):
    RealtimeLogger.info(f"Indexing {ref_fasta}")
    subprocess.run(f"bwa index {ref_fasta}", shell=True, check=True)
    subprocess.run(f"samtools faidx {ref_fasta}", shell=True, check=True)
    return ref_fasta

def align_reads(job, ref_fasta, fq1, sample_name):
    RealtimeLogger.info(f"Alignment {sample_name}")
    sam_out = f"{sample_name}.sam"
    cores = 10
    cmd = f"bwa mem -t {cores} {ref_fasta} {fq1} > {sam_out}"
    subprocess.run(cmd, shell=True, check=True, executable='/bin/bash')
    sam_id = job.fileStore.writeGlobalFile(sam_out)
    return sam_id

def samtools_view(job, sam_id, sample_name):
    RealtimeLogger.info(f"samtools view {sample_name}")
    sam_path = job.fileStore.readGlobalFile(sam_id)
    bam_unsorted = f"{sample_name}.unsorted.bam"
    subprocess.run(f"samtools view -bS {sam_path} > {bam_unsorted}", shell=True, check=True)
    bam_id = job.fileStore.writeGlobalFile(bam_unsorted)
    return bam_id

def qc_check(job, bam_id, sample_name):
    RealtimeLogger.info(f"flagstat QC for {sample_name}")
    bam_path = job.fileStore.readGlobalFile(bam_id)
    flagstat_out = f"{sample_name}.flagstat.txt"
    subprocess.run(f"samtools flagstat {bam_path} > {flagstat_out}", shell=True, check=True)

    percent = "0"
    with open(flagstat_out, 'r') as f:
        for line in f:
            if "mapped (" in line:
                percent = line.split('(')[1].split('%')[0]
                break

    RealtimeLogger.info(f"Mapping rate: {percent}%")
    if float(percent) > 90.0:
        RealtimeLogger.info("Flagstat state = OK")
        return bam_id   
    else:
        error_msg = f"Flagstat state = NOT OK, percentage = {percent}%. Stopping pipeline."
        RealtimeLogger.error(error_msg)
        raise RuntimeError(error_msg)

def sort_and_variant(job, bam_id, ref_fasta, sample_name):
    RealtimeLogger.info(f"Sorting BAM  {sample_name}")
    bam_path = job.fileStore.readGlobalFile(bam_id)
    bam_sorted = f"{sample_name}.sorted.bam"
    subprocess.run(f"samtools sort {bam_path} -o {bam_sorted}", shell=True, check=True)
    RealtimeLogger.info(f"Launching freebayes for {sample_name}")
    vcf_out = f"{sample_name}.vcf"
    cmd = f"freebayes -f {ref_fasta} -b {bam_sorted} > {vcf_out}"
    subprocess.run(cmd, shell=True, check=True, executable='/bin/bash')
    vcf_id = job.fileStore.writeGlobalFile(vcf_out)
    return vcf_id


def main():
    parser = Job.Runner.getDefaultArgumentParser()
    options = parser.parse_args()
    options.clean = "always"
    options.default_memory = "2G"
    options.default_cores = 10

    
    ref_fasta = os.path.join(SCRIPT_DIR, "GCF_000005845.2_ASM584v2_genomic.fna")
    fq1 = os.path.join(SCRIPT_DIR, "ERR15404843.fastq.gz")
    sample_name = "ERR15404843"

    root = Job()

    fastqc_job = root.addChildJobFn(run_fastqc, fq1)
    index_job = root.addChildJobFn(index_reference, ref_fasta)

  
    align_job = root.addFollowOnJobFn(align_reads, index_job.rv(), fq1, sample_name,
                                      preemptible=True)

    view_job = align_job.addChildJobFn(samtools_view, align_job.rv(), sample_name)

    qc_job = view_job.addChildJobFn(qc_check, view_job.rv(), sample_name)

    
    variant_job = qc_job.addChildJobFn(sort_and_variant, qc_job.rv(), ref_fasta, sample_name)
    

    with Toil(options) as toil:
        toil.start(root)

if __name__ == "__main__":
    main()
