#!/bin/bash
set -euo pipefail

# ===== Configuration =====
INPUT_DIR="./01.rawdata"
OUTPUT_DIR="./results"
THREADS=16
UNICYCLER_IMAGE="snailqh/unicycler"
BAKTA_IMAGE="oschwengers/bakta:latest"

# ===== Directory Setup =====
mkdir -p ${OUTPUT_DIR}/{02.cleanfastq,03.assemblies,04.quast_results,05.bakta_results}

# ===== 1. Quality Control with fastp =====
echo "=== STEP 1: FASTP QUALITY CONTROL ==="
for R1 in ${INPUT_DIR}/*.fastq.gz; do
    SAMPLE=$(basename ${R1} .fastq.gz)
    
    echo "Processing sample: ${SAMPLE}"
    
    zcat ${R1} | \
        NanoFilt -l 50 --headcrop 50 | \
        gzip > ${OUTPUT_DIR}/02.cleanfastq/${SAMPLE}.filtered.fastq.gz

    fastqc -t ${THREADS} \
        -o ${OUTPUT_DIR}/02.cleanfastq \
        ${OUTPUT_DIR}/02.cleanfastq/${SAMPLE}.filtered.fastq.gz
done

# ===== 2. Genome Assembly with Unicycler ===== 
echo "=== STEP 2: UNICYCLER ASSEMBLY ==="
for R1 in ${OUTPUT_DIR}/02.cleanfastq/*filtered.fastq.gz; do
    SAMPLE=$(basename ${R1} .filtered.fastq.gz)
    LONGREADS_PATH="${OUTPUT_DIR}/02.cleanfastq/${SAMPLE}.filtered.fastq.gz"
    echo "Assembling sample: ${SAMPLE}"
    
    docker run --rm \
      -v $(pwd):/data \
      ${UNICYCLER_IMAGE} \
      unicycler \
        -l /data/${LONGREADS_PATH} \
        -o /data/${OUTPUT_DIR}/03.assemblies/${SAMPLE} \
        --threads ${THREADS} \
        --mode bold \
        --keep 0
done

#prepare database for Bakta;

# ===== 3. Parallel QUAST Evaluation & Bakta Annotation ===== 
echo "=== STEP 3: PARALLEL QUAST & BAKTA PROCESSING ==="
for ASSEMBLY_FASTA in ${OUTPUT_DIR}/03.assemblies/*/assembly.fasta; do
    SAMPLE=$(basename $(dirname ${ASSEMBLY_FASTA}))
    
    echo "Launching QUAST evaluation: ${SAMPLE}"
    docker run -d --rm \
      -v $(pwd):/data \
      staphb/quast:5.3.0 \
      quast.py \
        /data/${ASSEMBLY_FASTA} \
        -o /data/${OUTPUT_DIR}/04.quast_results/${SAMPLE} \
        --gene-finding \
        --threads ${THREADS} \
        --min-contig 1000

    echo "Launching Bakta annotation: ${SAMPLE}"
    docker run -d --rm \
      -v $(pwd):/data \
      -v /data1/reference/bakta_db/db:/db \
      ${BAKTA_IMAGE} \
        --db /db \
        --output /data/${OUTPUT_DIR}/05.bakta_results/${SAMPLE} \
        --threads ${THREADS} \
        --prefix ${SAMPLE} \
        /data/${ASSEMBLY_FASTA}
done

