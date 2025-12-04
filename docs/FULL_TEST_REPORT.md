# Pipeline Test Report

**Generated:** 2025-12-03 18:04:35
**Output Directory:** `/data1/opt/nanopore_plasmid_pipeline/full_test_output`

---

## Executive Summary

✅ **Pipeline Status:** SUCCESS - All steps completed successfully

## Step-by-Step Analysis

### Step 0: Initialization

- ✅ Configuration file generated: `config.yaml` (562 bytes)

### Step 1: Assembly (epi2me wf-clone-validation)

- ✅ **FASTA files generated:** 11
- **Files:**
  - `sample03.final.fasta`
  - `sample04.final.fasta`
  - `sample05.final.fasta`
  - `sample02.final.fasta`
  - `sample06.final.fasta`
  - `sample09.final.fasta`
  - `sample11.final.fasta`
  - `sample10.final.fasta`
  - `sample12.final.fasta`
  - `sample08.final.fasta`
  - ... and 1 more
- ✅ Samplesheet generated

### Step 2: Fragment Splitting

- ✅ **Total fragments generated:** 22
- **Samples processed:** 11
- **Average fragments per sample:** 2.0

### Step 3: AB1 File Generation

- ✅ **Total AB1 files generated:** 22
- **Samples processed:** 11
- **Average AB1 files per sample:** 2.0

### Step 4: Report Generation

- ⚠️ No PDF reports found
- ⚠️ No JSON files found

## Log Analysis

### pipeline

- **File:** `/data1/opt/nanopore_plasmid_pipeline/full_test_output/logs/pipeline.log`
- **Size:** 198,076 bytes
- **Lines:** 3,284
- ⚠️ **Warnings:** 170
- ✅ **Key events:** 2
  - Line 3253: `Completed at: 03-Dec-2025 18:02:54...`
  - Line 3281: `[2025-12-03 18:03:23] Pipeline completed successfully!...`

### step0_initialize

- **File:** `/data1/opt/nanopore_plasmid_pipeline/full_test_output/logs/step0_initialize.log`
- **Size:** 3,294 bytes
- **Lines:** 56

## Output Directory Structure

```
├── 01.assembly
│   ├── .nextflow
│   │   ├── cache
│   │   ├── matplotlib
│   │   ├── plr
│   │   ├── tmp
│   │   └── history
│   ├── execution
│   │   ├── report.html
│   │   ├── timeline.html
│   │   └── trace.txt
│   ├── work
│   │   ├── 00
│   │   ├── 01
│   │   ├── 02
│   │   ├── 03
│   │   ├── 05
│   │   ├── 07
│   │   ├── 0b
│   │   ├── 0d
│   │   ├── 0f
│   │   ├── 12
│   │   ├── 13
│   │   ├── 14
│   │   ├── 15
│   │   ├── 16
│   │   ├── 19
│   │   ├── 1f
│   │   ├── 23
│   │   ├── 24
│   │   ├── 25
│   │   ├── 29
│   │   ├── 2a
│   │   ├── 2b
│   │   ├── 2e
│   │   ├── 2f
│   │   ├── 30
│   │   ├── 31
│   │   ├── 34
│   │   ├── 35
│   │   ├── 3c
│   │   ├── 3d
│   │   ├── 3e
│   │   ├── 40
│   │   ├── 41
│   │   ├── 43
│   │   ├── 44
│   │   ├── 46
│   │   ├── 4c
│   │   ├── 4d
│   │   ├── 4e
│   │   ├── 4f
│   │   ├── 50
│   │   ├── 51
│   │   ├── 54
│   │   ├── 55
│   │   ├── 57
│   │   ├── 59
│   │   ├── 5a
│   │   ├── 5b
│   │   ├── 5c
│   │   ├── 5d
│   │   ├── 5e
│   │   ├── 62
│   │   ├── 65
│   │   ├── 6a
│   │   ├── 6d
│   │   ├── 6e
│   │   ├── 6f
│   │   ├── 70
│   │   ├── 71
│   │   ├── 73
│   │   ├── 74
│   │   ├── 75
│   │   ├── 76
│   │   ├── 77
│   │   ├── 79
│   │   ├── 7a
│   │   ├── 7c
│   │   ├── 7f
│   │   ├── 81
│   │   ├── 84
│   │   ├── 85
│   │   ├── 87
│   │   ├── 8a
│   │   ├── 8b
│   │   ├── 8c
│   │   ├── 8d
│   │   ├── 90
│   │   ├── 91
│   │   ├── 93
│   │   ├── 94
│   │   ├── 95
│   │   ├── 97
│   │   ├── 9a
│   │   ├── 9b
│   │   ├── 9d
│   │   ├── 9f
│   │   ├── a1
│   │   ├── a2
│   │   ├── a4
│   │   ├── a5
│   │   ├── a6
│   │   ├── a8
│   │   ├── a9
│   │   ├── aa
│   │   ├── ab
│   │   ├── ad
│   │   ├── b2
│   │   ├── b5
│   │   ├── b8
│   │   ├── ba
│   │   ├── bb
│   │   ├── be
│   │   ├── c0
│   │   ├── c6
│   │   ├── c8
│   │   ├── cc
│   │   ├── cd
│   │   ├── ce
│   │   ├── cf
│   │   ├── collect-file
│   │   ├── d1
│   │   ├── d3
│   │   ├── d8
│   │   ├── d9
│   │   ├── db
│   │   ├── dc
│   │   ├── dd
│   │   ├── de
│   │   ├── e0
│   │   ├── e1
│   │   ├── e3
│   │   ├── e4
│   │   ├── e7
│   │   ├── ea
│   │   ├── ed
│   │   ├── ee
│   │   ├── f1
│   │   ├── f2
│   │   ├── f6
│   │   ├── f9
│   │   ├── fa
│   │   ├── fd
│   │   ├── fe
│   │   ├── ff
│   │   └── tmp
│   ├── .nextflow.log
│   ├── feature_table.txt
│   ├── nextflow.config.override
│   ├── plannotate.json
│   ├── plannotate_report.json
│   ├── sample02.annotations.bed
│   ├── sample02.annotations.gbk
│   ├── sample02.assembly.maf
│   ├── sample02.assembly_stats.tsv
│   ├── sample02.final.fasta
│   ├── sample02.final.fastq
│   ├── sample02.insert.fasta
│   ├── sample03.annotations.bed
│   ├── sample03.annotations.gbk
│   ├── sample03.assembly.maf
│   ├── sample03.assembly_stats.tsv
│   ├── sample03.final.fasta
│   ├── sample03.final.fastq
│   ├── sample03.insert.fasta
│   ├── sample04.annotations.bed
│   ├── sample04.annotations.gbk
│   ├── sample04.assembly.maf
│   ├── sample04.assembly_stats.tsv
│   ├── sample04.final.fasta
│   ├── sample04.final.fastq
│   ├── sample04.insert.fasta
│   ├── sample05.annotations.bed
│   ├── sample05.annotations.gbk
│   ├── sample05.assembly.maf
│   ├── sample05.assembly_stats.tsv
│   ├── sample05.final.fasta
│   ├── sample05.final.fastq
│   ├── sample05.insert.fasta
│   ├── sample06.annotations.bed
│   ├── sample06.annotations.gbk
│   ├── sample06.assembly.maf
│   ├── sample06.assembly_stats.tsv
│   ├── sample06.final.fasta
│   ├── sample06.final.fastq
│   ├── sample06.insert.fasta
│   ├── sample07.annotations.bed
│   ├── sample07.annotations.gbk
│   ├── sample07.assembly.maf
│   ├── sample07.assembly_stats.tsv
│   ├── sample07.final.fasta
│   ├── sample07.final.fastq
│   ├── sample07.insert.fasta
│   ├── sample08.annotations.bed
│   ├── sample08.annotations.gbk
│   ├── sample08.assembly.maf
│   ├── sample08.assembly_stats.tsv
│   ├── sample08.final.fasta
│   ├── sample08.final.fastq
│   ├── sample08.insert.fasta
│   ├── sample09.annotations.bed
│   ├── sample09.annotations.gbk
│   ├── sample09.assembly.maf
│   ├── sample09.assembly_stats.tsv
│   ├── sample09.final.fasta
│   ├── sample09.final.fastq
│   ├── sample09.insert.fasta
│   ├── sample10.annotations.bed
│   ├── sample10.annotations.gbk
│   ├── sample10.assembly.maf
│   ├── sample10.assembly_stats.tsv
│   ├── sample10.final.fasta
│   ├── sample10.final.fastq
│   ├── sample10.insert.fasta
│   ├── sample11.annotations.bed
│   ├── sample11.annotations.gbk
│   ├── sample11.assembly.maf
│   ├── sample11.assembly_stats.tsv
│   ├── sample11.final.fasta
│   ├── sample11.final.fastq
│   ├── sample11.insert.fasta
│   ├── sample12.annotations.bed
│   ├── sample12.annotations.gbk
│   ├── sample12.assembly.maf
│   ├── sample12.assembly_stats.tsv
│   ├── sample12.final.fasta
│   ├── sample12.final.fastq
│   ├── sample12.insert.fasta
│   ├── sample_sheet.csv
│   ├── sample_status.txt
│   ├── samplesheet.csv
│   └── wf-clone-validation-report.html
├── 02.fragments
│   ├── logs
│   │   └── step2_split_fragments.log
│   ├── sample02_2k_fragmented
│   │   ├── sample02_part1.fasta
│   │   └── sample02_part2.fasta
│   ├── sample03_2k_fragmented
│   │   ├── sample03_part1.fasta
│   │   └── sample03_part2.fasta
│   ├── sample04_2k_fragmented
│   │   ├── sample04_part1.fasta
│   │   └── sample04_part2.fasta
│   ├── sample05_2k_fragmented
│   │   ├── sample05_part1.fasta
│   │   └── sample05_part2.fasta
│   ├── sample06_2k_fragmented
│   │   ├── sample06_part1.fasta
│   │   └── sample06_part2.fasta
│   ├── sample07_2k_fragmented
│   │   ├── sample07_part1.fasta
│   │   └── sample07_part2.fasta
│   ├── sample08_2k_fragmented
│   │   ├── sample08_part1.fasta
│   │   └── sample08_part2.fasta
│   ├── sample09_2k_fragmented
│   │   ├── sample09_part1.fasta
│   │   └── sample09_part2.fasta
│   ├── sample10_2k_fragmented
│   │   ├── sample10_part1.fasta
│   │   └── sample10_part2.fasta
│   ├── sample11_2k_fragmented
│   │   ├── sample11_part1.fasta
│   │   └── sample11_part2.fasta
│   └── sample12_2k_fragmented
│       ├── sample12_part1.fasta
│       └── sample12_part2.fasta
├── 03.ab1_files
│   ├── logs
│   │   └── step3_generate_ab1.log
│   ├── sample02_ab1
│   │   ├── sample02_part1.ab1
│   │   └── sample02_part2.ab1
│   ├── sample03_ab1
│   │   ├── sample03_part1.ab1
│   │   └── sample03_part2.ab1
│   ├── sample04_ab1
│   │   ├── sample04_part1.ab1
│   │   └── sample04_part2.ab1
│   ├── sample05_ab1
│   │   ├── sample05_part1.ab1
│   │   └── sample05_part2.ab1
│   ├── sample06_ab1
│   │   ├── sample06_part1.ab1
│   │   └── sample06_part2.ab1
│   ├── sample07_ab1
│   │   ├── sample07_part1.ab1
│   │   └── sample07_part2.ab1
│   ├── sample08_ab1
│   │   ├── sample08_part1.ab1
│   │   └── sample08_part2.ab1
│   ├── sample09_ab1
│   │   ├── sample09_part1.ab1
│   │   └── sample09_part2.ab1
│   ├── sample10_ab1
│   │   ├── sample10_part1.ab1
│   │   └── sample10_part2.ab1
│   ├── sample11_ab1
│   │   ├── sample11_part1.ab1
│   │   └── sample11_part2.ab1
│   └── sample12_ab1
│       ├── sample12_part1.ab1
│       └── sample12_part2.ab1
├── 04.reports
│   ├── logs
│   │   └── step4_generate_reports.log
│   ├── sample02
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample02.insert
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample03
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample03.insert
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample04
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample04.insert
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample05
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample05.insert
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample06
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample06.insert
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample07
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample07.insert
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample08
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample08.insert
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample09
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample09.insert
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample10
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample10.insert
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample11
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample11.insert
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample12
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   ├── sample12.insert
│   │   ├── CHROMATOGRAM_FILES_ab1
│   │   ├── FASTA_FILES
│   │   ├── PER_BASE_BREAKDOWN
│   │   ├── QC_REPORTS
│   │   └── RAW_FASTQ_FILES
│   └── full_test_summary.csv
├── 05.summary
├── logs
│   ├── pipeline.log
│   └── step0_initialize.log
├── config.yaml
└── pipeline_console.log
```

## Statistics Summary

| Metric | Value |
|--------|-------|
| FASTA files | 11 |
| Fragment directories | 11 |
| Total fragments | 22 |
| AB1 sample directories | 11 |
| Total AB1 files | 22 |
| PDF reports | 0 |
| JSON files | 0 |
| Log files | 2 |
