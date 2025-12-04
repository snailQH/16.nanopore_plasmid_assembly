# Project Structure

## Directory Organization

```
16.nanopore_plasmid_assembly/
├── README.md                    # Main entry point
├── CHANGE_LOGS.md              # Change history
├── environment.yml              # Conda environment definition
│
├── .cursor/                     # Cursor IDE configuration
│   └── rules/                   # Cursor rules
│       └── nanopore_plasmid_assembly.mdc
│
├── docs/                        # Documentation
│   ├── PIPELINE.md             # Pipeline documentation
│   ├── PROJECT_STRUCTURE.md    # This file
│   ├── DOCKER.md               # Docker setup (to be created)
│   ├── USAGE.md                # Usage guide (to be created)
│   └── TROUBLESHOOTING.md      # Troubleshooting (to be created)
│
├── scripts/                     # All pipeline scripts
│   ├── step0_initialize_analysis.py    # Step 0: Initialization
│   ├── step1_run_epi2me_workflow.py   # Step 1: Assembly
│   ├── step2_split_fragments.py       # Step 2: Fragmentation
│   ├── step3_generate_ab1.py          # Step 3: AB1 generation
│   ├── step4_generate_reports.py      # Step 4: Reports
│   ├── step5_summarize_results.py     # Step 5: Summary
│   ├── run_pipeline.py                 # Main entry script
│   ├── split_plasmid_fasta.py          # Existing fragmentation script
│   ├── generate_complete_reports.py   # Existing report generator
│   ├── generate_coverage_reports.py   # Coverage calculation
│   ├── get_length_dist_from_fastq.py   # Read length distribution
│   └── utils/                          # Utility functions
│       ├── __init__.py
│       ├── epi2me_wrapper.py
│       ├── hyraxabif_wrapper.py
│       └── config_manager.py
│
├── config/                      # Configuration files
│   └── config.yaml              # Pipeline configuration (auto-generated)
│
├── templates/                   # Report templates
│   └── report_template.html    # HTML report template
│
├── archive/                     # Archived old files
│   ├── old_pipeline/            # Old pipeline code
│   ├── old_scripts/            # Old scripts
│   ├── old_data/               # Old data files
│   └── old_docs/               # Old documentation
│
├── logs/                        # Log files (created at runtime)
│
└── output/                      # Output directory (created at runtime)
    ├── 01.assembly/            # epi2me workflow results
    ├── 02.fragments/           # Fragmented FASTA files
    ├── 03.ab1_files/           # AB1 chromatogram files
    ├── 04.reports/             # PDF reports
    ├── 05.summary/             # Summary JSON and plots
    └── logs/                   # Step-specific logs
```

## Key Directories

### `scripts/`
Contains all executable scripts for the pipeline:
- **Step scripts**: `step0_*.py` through `step5_*.py`
- **Main entry**: `run_pipeline.py`
- **Utility scripts**: Existing scripts for fragmentation, reporting, etc.
- **Utils**: Shared utility functions

### `docs/`
Documentation directory:
- Pipeline documentation
- Usage guides
- Troubleshooting
- Docker setup

### `config/`
Configuration files:
- `config.yaml`: Auto-generated pipeline configuration

### `archive/`
Archived files from previous versions:
- Old pipeline code
- Old scripts
- Old data files
- Old documentation

### `output/` (runtime)
Created during pipeline execution:
- Step-specific output directories
- Log files
- Final reports

## File Naming Conventions

### Scripts
- Step scripts: `step{N}_{description}.py`
- Main scripts: `{function_name}.py`
- Utility scripts: `{function_name}.py`

### Output Files
- Assembly: `{sample}.final.fasta`, `{sample}.final.fastq`
- Fragments: `{sample}_{contig}_part{N}.fasta`
- AB1 files: `{sample}_{contig}_part{N}.ab1`
- Reports: `{sample}_report.pdf`

### Configuration
- Config file: `config.yaml`
- Log files: `{step_name}_{timestamp}.log`

## Standards

### Code Organization
- Use relative paths in scripts
- Follow step-based architecture
- Implement proper error handling
- Generate comprehensive logs

### Documentation
- All documentation in `docs/`
- README.md as main entry point
- Change logs in `CHANGE_LOGS.md`
- Inline code comments in English

### Version Control
- Track all scripts and documentation
- Archive old versions in `archive/`
- Maintain change logs

