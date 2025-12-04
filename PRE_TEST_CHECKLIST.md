# Pre-Test Checklist

## ✅ Completed Checks

### 1. Docker Image
- ✅ Dockerfile builds successfully
- ✅ All dependencies installed (Nextflow, Haskell Stack, hyraxAbif, Python packages)
- ✅ Image size: 6.59GB
- ✅ hyraxAbif executable path: `/opt/hyraxAbif/hyraxAbif-exe` (correct)

### 2. Samplesheet Format
- ✅ Format: `barcode`, `alias`, `type` columns (matches epi2me requirements)
- ✅ Generated correctly from fast_pass directory structure
- ✅ Tested: 7 samples found and processed

### 3. epi2me Workflow Integration
- ✅ Command parameters:
  - `--fastq`: Parent directory (fast_pass)
  - `--sample_sheet`: CSV file mapping barcodes to aliases
  - `--out_dir`: Output directory (01.assembly/)
  - `--assm_coverage`: Correct parameter name (not `--coverage`)
  - `--approx_size`: Plasmid size estimate
  - `-profile docker`: For containerized execution
  - `-resume`: Allow resume if interrupted

### 4. Data Flow Between Steps
- ✅ Step 0 → Step 1: config.yaml passed correctly
- ✅ Step 1 → Step 2: 
  - Output: `01.assembly/` directory
  - Files: `{alias}.final.fasta`, `{alias}.final.fastq` (in out_dir root)
  - Step2 uses `rglob('*.final.fasta')` to find files recursively
- ✅ Step 2 → Step 3:
  - Output: `02.fragments/{sample}_2k_fragmented/` directories
  - Step3 looks for `*_fragmented` directories
- ✅ Step 3 → Step 4:
  - Output: `03.ab1_files/{sample}_ab1/` directories
  - Step4 needs FASTA and FASTQ files from Step 1

### 5. File Paths and Naming
- ✅ hyraxAbif executable: `/opt/hyraxAbif/hyraxAbif-exe` (exists in Docker)
- ✅ Sample naming: Extracted from directory names or file names
- ✅ Fragment directories: `{sample}_2k_fragmented` pattern
- ✅ AB1 directories: `{sample}_ab1` pattern

### 6. Configuration Consistency
- ✅ `coverage` parameter in config.yaml → converted to `assm_coverage` for epi2me
- ✅ `approx_size` passed correctly
- ✅ `fragment_size` default: 2000 bp
- ✅ `assembly_tool` default: 'flye'

### 7. Error Handling
- ✅ All steps have try-except blocks
- ✅ Error messages are clear and actionable
- ✅ Logging configured for all steps
- ✅ File existence checks where needed

## ⚠️ Potential Issues to Monitor

### 1. epi2me Output Structure
- **Expected**: Files directly in `out_dir` as `{alias}.final.fasta`
- **Actual**: Need to verify after first run
- **Mitigation**: Step2 uses recursive search (`rglob`) which should handle any structure

### 2. hyraxAbif Path
- **Docker**: `/opt/hyraxAbif/hyraxAbif-exe` (should exist)
- **Check**: Verify executable exists and is executable
- **Mitigation**: Error handling will catch if missing

### 3. Sample Name Extraction
- **Step2**: Extracts from file path (may need adjustment based on actual epi2me output)
- **Step3**: Extracts from directory name (`{sample}_2k_fragmented`)
- **Mitigation**: Both have fallback logic

### 4. Docker Volume Mounts
- **Input**: `/data/input/fast_pass:ro` (read-only)
- **Output**: `/data/output` (read-write)
- **Docker socket**: May be needed for epi2me's docker profile

## 🧪 Test Plan

1. **Initialization Test** ✅ (Completed)
   - Config generation
   - Directory structure creation
   - Samplesheet generation

2. **Full Pipeline Test** (Next)
   - Run complete pipeline
   - Monitor each step
   - Verify outputs at each stage
   - Check for errors and warnings

3. **Output Verification**
   - Check epi2me output structure
   - Verify fragment files exist
   - Verify AB1 files generated
   - Verify reports generated

## 📝 Notes

- epi2me workflow may take significant time (6 minutes per sample for 10,000 reads)
- Docker profile requires Docker socket access (`-v /var/run/docker.sock:/var/run/docker.sock`)
- All scripts use relative paths where possible for portability

