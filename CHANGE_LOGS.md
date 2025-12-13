# Change Logs

All changes, updates, and improvements to the Nanopore Plasmid Assembly Pipeline.

## 2025-12-13 - Add Nextflow Config Override for Docker Executor

### Problem:
- Nextflow workflow still failing with `/bin/bash: .command.run: No such file or directory`
- Docker executor cannot access work directory in Docker-in-Docker scenario
- Need proper Docker executor configuration for processes

### Solution:
- Added Nextflow config override file with explicit Docker executor settings
- Enabled `fixOwnership` for Docker executor to handle file permissions
- Used absolute paths for work directory throughout
- Added Docker executor configuration in config override

### Files Modified:
- `scripts/step1_run_epi2me_workflow.py`:
  - Added Docker executor configuration in Nextflow config override
  - Enabled `fixOwnership` for proper file permission handling
  - Improved logging for work directory paths

### Key Changes:
- Docker executor: Explicitly configured in Nextflow config
- File permissions: Enabled `fixOwnership` to handle permission issues
- Path handling: Using absolute paths consistently

### Impact:
- Better Docker executor configuration for Docker-in-Docker scenarios
- Should resolve work directory access issues

## 2025-12-13 - Fix Nextflow Work Directory Configuration in Docker

### Problem:
- Nextflow workflow failed with error: `/bin/bash: .command.run: No such file or directory`
- Exit status 127 indicates Nextflow cannot create or access work files
- Work directory path `/data/work/` may not be accessible or writable in Docker container

### Solution:
- Set explicit Nextflow work directory using `-work-dir` parameter
- Set `NXF_WORK` environment variable to output directory
- Change working directory to output path before running Nextflow
- Set `NXF_TEMP` and `MPLCONFIGDIR` environment variables for proper temp directory handling

### Files Modified:
- `scripts/step1_run_epi2me_workflow.py`:
  - Added `NXF_WORK` environment variable setting
  - Added `NXF_TEMP` and `MPLCONFIGDIR` environment variables
  - Changed working directory to output path before running Nextflow
  - Added `-work-dir` parameter to Nextflow command
  - Added proper directory restoration in finally block

### Key Changes:
- Work directory: Explicitly set to `output_dir/work` instead of default `/data/work`
- Temp directory: Set to `output_dir/.nextflow/tmp`
- Working directory: Change to output path ensures relative paths work correctly
- Environment: Proper cleanup with directory restoration

### Impact:
- Nextflow can now create work files in the correct writable location
- Prevents "No such file or directory" errors
- Better isolation of Nextflow work directories per pipeline run

## 2025-12-13 - Fix Read-Only File System Issue for Barcode Directory Creation

### Problem:
- When input directory is mounted as read-only (`:ro`), `generate_samplesheet.py` fails to create barcode directories
- Error: `[Errno 30] Read-only file system: '/data/input/barcode01'`
- Barcode directories need to be created for Nextflow workflow, but input directory is read-only

### Solution:
- Added `--work-dir` parameter to `generate_samplesheet.py` to specify where barcode directories should be created
- Modified `step1_run_epi2me_workflow.py` to create a `fastq_processed` directory in output for barcode directories
- Barcode directories are now created in output directory instead of input directory
- Nextflow workflow uses the processed fastq directory if barcode directories exist there

### Files Modified:
- `scripts/generate_samplesheet.py`: 
  - Added `work_dir` parameter to specify where barcode directories should be created
  - Modified barcode directory creation logic to use `work_dir` if provided
  - Added `--work-dir` command-line argument
- `scripts/step1_run_epi2me_workflow.py`: 
  - Modified `generate_samplesheet()` to accept and pass `work_dir` parameter
  - Creates `fastq_processed` directory in output for barcode directories
  - Uses processed fastq directory for Nextflow if barcode directories exist there

### Key Changes:
- Work directory: Creates `01.assembly/fastq_processed/` for barcode directories
- Read-only support: Input directory can now be read-only
- Automatic detection: Uses processed directory if barcode directories exist, otherwise uses original

### Impact:
- Supports read-only input directory mounting in Docker
- Barcode directories created in writable output directory
- No changes needed to Docker run command (works automatically)

## 2025-12-13 - Enable Assembly Step in Docker Container Mode

### Problem:
- When running `run_pipeline.py` inside Docker container, assembly step was automatically skipped
- Error: "Assembly results not found. Please run run_pipeline.sh first."
- Even with Docker socket mounted, assembly couldn't run inside Docker

### Solution:
- Modified `run_pipeline.py` to detect Docker environment and Docker socket availability
- If Docker socket is available, assembly can now run inside Docker container
- If Docker socket is not available, provides clear error message with solutions

### Files Modified:
- `scripts/run_pipeline.py`: 
  - Added Docker environment detection (`/.dockerenv`)
  - Added Docker socket detection (`/var/run/docker.sock`)
  - Modified Step 1 logic to run assembly if Docker socket is available
  - Provides helpful error messages if Docker socket is missing

### Key Changes:
- Detection: Checks for `/.dockerenv` and `/var/run/docker.sock`
- Logic: Runs assembly if Docker socket is available, otherwise provides helpful errors
- User experience: Clear messages about what's needed to run assembly in Docker

### Impact:
- Full pipeline can now run inside Docker container with Docker socket mounted
- Better error messages when Docker socket is missing
- Supports both HOST and Docker execution modes seamlessly

## 2025-12-12 - Fixed FASTQ File Merging and Nextflow Directory Conflicts

### Problem:
1. **Multiple FASTQ files per sample**: Some sample directories contain multiple `fastq.gz` files that need to be merged before analysis
2. **Nextflow directory conflicts**: Creating symbolic links for barcode mapping caused Nextflow to see both original directories and symlinks, resulting in "Found conflicting folders" error
3. **Input directory detection**: Pipeline couldn't properly detect data in `*-Raw/` subdirectories (e.g., `CT121125GS-Raw/`)

### Solution:
1. **Added FASTQ merging**: Modified `generate_samplesheet.py` to automatically merge multiple `fastq.gz` files per sample using `zcat` and `gzip`
2. **Replaced symlinks with directories**: Instead of creating symbolic links, now creates new barcode-named directories with merged FASTQ files to avoid Nextflow conflicts
3. **Improved input detection**: Enhanced `run_pipeline.sh` to detect `*-Raw/` project directories and handle nested sample directory structures

### Files Modified:
- `scripts/generate_samplesheet.py`: 
  - Added `merge_fastq_files()` function to merge multiple FASTQ.gz files
  - Changed from symlink creation to directory creation with merged files
  - Added handling for existing directories and symlinks
- `run_pipeline.sh`: 
  - Improved FASTQ directory detection to handle `*-Raw/` subdirectories
  - Updated comments to reflect new merging behavior instead of symlink creation

### Key Changes:
- Merge logic: Uses `zcat file1.gz file2.gz ... | gzip > merged.gz` to combine FASTQ files
- Directory strategy: Creates new `barcodeXX/` directories with merged files instead of symlinks
- Conflict prevention: Removes existing symlinks before creating directories
- Input flexibility: Supports `input_dir/fastq/`, `input_dir/fast_pass/`, `input_dir/*-Raw/`, and direct sample directories

### Impact:
- Resolves "Found conflicting folders" errors from Nextflow
- Automatically handles samples with multiple FASTQ files
- Supports more flexible input directory structures
- Preserves original data (only creates new directories/files, doesn't modify originals)

## 2025-12-09 - Added Automatic Nextflow Lock File Cleanup

### Problem:
- Nextflow workflow failed with error: "Unable to acquire lock on session"
- This occurs when a previous execution was interrupted, leaving lock files in `.nextflow/cache/` directory

### Solution:
- Added automatic lock file detection and cleanup before running Nextflow
- Checks for stale lock files in `.nextflow/cache/` directory
- Verifies no running Nextflow processes before cleaning locks
- Prevents interference with active Nextflow runs

### Files Modified:
- `run_pipeline.sh`: Added lock file cleanup logic before Nextflow execution (lines ~387-410)

### Key Changes:
- Check for lock files: `find $LOCK_DIR -name "LOCK" -type f`
- Verify no running processes: `pgrep -f "nextflow.*wf-clone-validation"`
- Auto-clean stale locks if no processes are running
- Warn and exit if processes are running (safety check)

### Manual Fix (if needed):
If automatic cleanup doesn't work, manually clean lock files:
```bash
find /path/to/output/01.assembly/.nextflow/cache -name "LOCK" -type f -delete
```

### Impact:
- Prevents "Unable to acquire lock" errors from interrupted runs
- Automatic recovery from failed/interrupted executions
- Safe: Won't interfere with running Nextflow processes

## 2025-12-03 - Reverted to Local Docker Build and Created Delivery Package

### Updates:
- **Reverted Docker image**: Changed back to local build (`nanopore-plasmid-pipeline:latest`)
- **Removed Docker Hub references**: All documentation now uses local build
- **Created delivery package**: Added `DELIVERY_PACKAGE.md` with file list and instructions
- **Created installation guide**: Added `INSTALLATION.md` with detailed installation steps

### Files Modified:
- `run_pipeline.sh`: Reverted to use local Docker image only
- `README.md`: Updated to use local build instructions
- `docs/USER_GUIDE.md`: Removed Docker Hub references, updated to local build
- `DELIVERY_PACKAGE.md`: New file - delivery package contents and structure
- `INSTALLATION.md`: New file - detailed installation guide

### Files Created:
- `DELIVERY_PACKAGE.md`: Complete delivery package documentation
- `INSTALLATION.md`: Step-by-step installation guide

### Key Changes:
- Docker image: `nanopore-plasmid-pipeline:latest` (local build only)
- Removed Docker Hub image references
- Added comprehensive installation documentation
- Created delivery package checklist

## 2025-12-03 - Clarified Pipeline Architecture and Execution Modes

### Updates:
- **Architecture clarification**: Documented the hybrid architecture (HOST + Docker)
- **Execution modes**: Clarified two execution modes:
  1. `run_pipeline.sh` - Full pipeline (recommended)
  2. `run_pipeline.py` - Docker-only (Steps 2-4 only, requires existing assembly)
- **Nextflow execution**: Clarified that Nextflow runs on HOST machine, not in Docker
- **Why Nextflow on HOST**: Explained Docker socket access requirement

### Files Modified:
- `docs/USER_GUIDE.md`: 
  - Added architecture overview section
  - Clarified execution modes
  - Updated Step 1 description to explain HOST execution
  - Added examples for both execution modes
  - Updated Docker image information section

### Key Points:
- Nextflow runs on HOST because it needs Docker socket access
- `run_pipeline.sh` orchestrates HOST and Docker execution
- `run_pipeline.py` is Docker-only and skips assembly
- Docker image contains all scripts but NOT Nextflow

## 2025-12-03 - Updated Documentation for Docker Hub Image

### Updates:
- **Docker Hub Image**: Updated all documentation to use pre-built Docker Hub image
- **Image Name**: `snailqh/nanopore-plasmid-pipeline:ampseq`
- **Image Size**: ~6.7 GB
- **Default Behavior**: Pipeline script now uses Docker Hub image by default

### Files Modified:
- `docs/USER_GUIDE.md`: Updated installation section to prioritize Docker Hub image
- `README.md`: Updated quick start to use Docker Hub image
- `run_pipeline.sh`: Updated to use Docker Hub image by default with fallback to local image

### Benefits:
- Users no longer need to build Docker image locally
- Faster setup (pull vs build)
- Consistent image across all users
- Easier deployment

## 2025-12-03 - Created User Documentation

### Documentation Added:
- **USER_GUIDE.md**: Comprehensive user guide (19KB) with:
  - Installation instructions
  - Detailed usage examples
  - Command-line argument reference
  - Input data requirements
  - Pipeline step descriptions
  - Troubleshooting guide
  - Best practices and performance tips
- **OUTPUT_FORMAT.md**: Complete output format documentation (19KB) with:
  - Output directory structure
  - File format descriptions
  - Report structure details
  - Summary file formats
  - Data interpretation guide
  - Quality metrics explanation
  - Compatibility information

### Files Created:
- `docs/USER_GUIDE.md`: User guide (comprehensive, 19KB)
- `docs/OUTPUT_FORMAT.md`: Output format documentation (detailed, 19KB)

### Files Modified:
- `README.md`: Added links to new documentation

### Purpose:
These documents are designed for end users who will use the pipeline. They provide:
- Step-by-step instructions for installation and usage
- Complete parameter reference with examples
- Output interpretation guide
- Troubleshooting assistance
- Examples for common use cases

## 2025-12-03 - Fixed Nextflow path resolution issue

### Issue Fixed:
- **Nextflow path resolution**: When Nextflow is found via `command -v`, script was setting `NEXTFLOW_CMD="nextflow"` (command name only), but then checking `[[ ! -f "$NEXTFLOW_CMD" ]]` which fails because `nextflow` is not a file path
- **Solution**: Use `which nextflow` to get the full path and set `NEXTFLOW_CMD` to the full path

### Files Modified:
- `run_pipeline.sh`: Changed `NEXTFLOW_CMD="nextflow"` to `NEXTFLOW_CMD=$(which nextflow)` (line 260)

### Testing:
- Nextflow found in PATH will now use full path for verification

## 2025-12-03 - Fixed Nextflow installation and improved logging

### Issues Fixed:

1. **Nextflow installation location**
   - **Problem**: Nextflow was being installed to SCRIPT_DIR, which may not have write permissions
   - **Solution**: Install Nextflow to OUTPUT_DIR/01.assembly instead, which is user-specified and should have write permissions
   - **Benefit**: Avoids permission issues and keeps Nextflow with the project output

2. **Nextflow verification**
   - **Problem**: Script didn't verify Nextflow actually works after finding/installing it
   - **Solution**: Added version check after finding/installing Nextflow to ensure it's functional

3. **Log file directory creation**
   - **Problem**: LOG_FILE directory might not exist when log() is first called
   - **Solution**: Explicitly create logs directory before defining log() function

### Files Modified:
- `run_pipeline.sh`:
  - Changed Nextflow installation location from SCRIPT_DIR to OUTPUT_DIR/01.assembly (line 291-299)
  - Added Nextflow version verification after installation (line 305-310)
  - Added explicit logs directory creation (line 150)

### Testing:
- Nextflow will now be installed to output directory if not found
- Version check ensures Nextflow is functional before use

## 2025-12-03 - Fixed output directory creation issue (final fix)

### Issue Fixed:
- **Output directory not created before log redirection**: When users redirect logs to a file in the output directory (e.g., `> output_dir/pipeline_console.log`), the directory must exist **before shell processes the redirection**. Shell processes redirections before script execution, so we need to create the directory during argument parsing.

### Solution:
- Create output directory **immediately** when `--output` parameter is parsed (in the argument parsing loop)
- This ensures the directory exists before shell tries to open the log file for redirection

### Files Modified:
- `run_pipeline.sh`: Added `mkdir -p "$OUTPUT_DIR"` in the `--output|-o` case handler (line 35-39)

### Testing:
- Script now creates output directory during argument parsing
- Log redirection to output directory now works correctly even if directory doesn't exist

## 2025-12-03 - Fixed Nextflow chmod error and improved error handling

### Issue Fixed:
- **Nextflow chmod error**: Script was trying to chmod a non-existent nextflow file when `$NEXTFLOW_CMD` was empty or file didn't exist
- **Solution**: Added validation checks before chmod operation:
  - Check if `$NEXTFLOW_CMD` is empty
  - Check if file exists before chmod
  - Provide clear error messages and exit on failure

### Files Modified:
- `run_pipeline.sh`: Added validation checks before chmod operation (lines 278-290)

### Testing:
- First test (final_test_output) completed successfully ✅
  - AB1 files correctly copied to `04.reports/sample/CHROMATOGRAM_FILES_ab1/`
  - FASTQ files only contain `.fastq.gz` files (no uncompressed `.fastq`)
  - All pipeline steps completed successfully
- Second test (fast_pass_test_output) should now work with improved error handling

## 2025-12-03 - Fixed AB1 file copying, FASTQ file handling, and assembly_dir parameter

### Issues Fixed:
1. **AB1 files not copied to report directories**: Added logic to copy AB1 files from `03.ab1_files/{sample}_ab1/` to `04.reports/{sample}/CHROMATOGRAM_FILES_ab1/`
2. **FASTQ files**: Modified to only keep `.fastq.gz` files in `RAW_FASTQ_FILES/`, removing uncompressed `.fastq` files
3. **Missing `--assembly-dir` parameter**: Added `--assembly-dir` and `--ab1-dir` arguments to `generate_complete_reports.py`

### Files Modified:
- `scripts/generate_complete_reports.py`:
  - Added `--assembly-dir` and `--ab1-dir` command-line arguments
  - Modified `organize_files_by_sample_per_sample_structure()` to accept `ab1_dir` parameter
  - Added logic to copy AB1 files from `ab1_dir/{sample}_ab1/` to `CHROMATOGRAM_FILES_ab1/` directory
  - Modified FASTQ file handling to only create `.fastq.gz` files (removed uncompressed `.fastq` files)
- `scripts/step4_generate_reports.py`:
  - Updated `generate_reports()` function to accept `ab1_dir` parameter
  - Added `--ab1-dir` argument to command-line interface
  - Pass `ab1_dir` to `generate_complete_reports.py`
- `scripts/run_pipeline.py`:
  - Updated call to `step4.generate_reports()` to pass `ab1_dir` parameter

### Testing:
- Docker image rebuilt successfully
- Ready for full pipeline test


All changes, updates, and improvements to the Nanopore Plasmid Assembly Pipeline.

## 2025-12-03 - Fixed Three Pipeline Issues

### Issues Fixed

1. **Nextflow work directory cleanup**
   - Problem: Nextflow work directory contains intermediate files that consume disk space
   - Solution: Added cleanup step in `run_pipeline.sh` to remove `work/` directory after assembly completes
   - Files Modified: `run_pipeline.sh`

2. **Insert sequence folders in reports**
   - Problem: `sample02.insert/` folders were being created in report output because `.insert.fasta` files were being processed
   - Solution: Modified `generate_complete_reports.py` to filter out `.insert.fasta` files when organizing samples
   - Files Modified: `scripts/generate_complete_reports.py`

3. **CSV file circularity information**
   - Problem: CSV file always showed `Is Circular: False` (hardcoded) instead of reading from GenBank files
   - Solution: 
     - Added `read_circularity_from_gbk()` function to read circularity from GenBank LOCUS line
     - Modified `generate_summary_csv()` to accept `assembly_dir` parameter and read circularity from `.annotations.gbk` files
     - Updated `step4_generate_reports.py` and `run_pipeline.py` to pass `assembly_dir` parameter
   - Files Modified:
     - `scripts/generate_complete_reports.py`
     - `scripts/step4_generate_reports.py`
     - `scripts/run_pipeline.py`

### Testing
- All fixes tested and verified
- Work directory cleanup reduces disk usage
- Insert folders no longer created
- CSV file now correctly shows circularity from GenBank files

## 2025-12-03 - Full Pipeline Test - SUCCESS

### Test Execution
- **Test Date:** 2025-12-03
- **Test ID:** full_test
- **Input:** `/data1/opt/nanopore_plasmid_pipeline/wf-clone-validation-demo/fastq` (12 samples)
- **Output:** `/data1/opt/nanopore_plasmid_pipeline/full_test_output`
- **Status:** ✅ SUCCESS - All steps completed successfully

### Test Results
- **Runtime:** ~4 minutes 33 seconds
- **Samples Processed:** 11 out of 12 (sample01 filtered out)
- **FASTA Files Generated:** 11
- **Fragments Generated:** 22 (2 per sample)
- **AB1 Files Generated:** 22 (2 per sample)
- **PDF Reports Generated:** 11

### Pipeline Steps Verified
1. ✅ **Step 0: Initialization** - Configuration generated successfully
2. ✅ **Step 1: Assembly** - epi2me wf-clone-validation completed (11 FASTA files)
3. ✅ **Step 2: Fragment Splitting** - All samples fragmented correctly
4. ✅ **Step 3: AB1 Generation** - All fragments converted to AB1 format
5. ✅ **Step 4: Report Generation** - All reports generated successfully

### Key Observations
- All pipeline steps executed in correct order
- All dependencies satisfied
- Outputs properly organized
- No critical errors in logs
- hyraxAbif working correctly after Docker fix

### Files Created
- `docs/FULL_TEST_REPORT.md`: Comprehensive test report
- `docs/PIPELINE_EXECUTION_LOG.md`: Detailed execution log
- `scripts/generate_test_report.py`: Test report generation script

### Documentation
- Test report includes step-by-step analysis
- Execution log documents timeline and statistics
- Report generation script can be reused for future tests

## 2025-12-03 - Fixed hyraxAbif Installation in Dockerfile

### Problem
- The `hyraxAbif-exe` file in `/opt/hyraxAbif/hyraxAbif-exe` was only a 40-byte shell script wrapper, not the actual compiled executable
- The actual executable (3.4MB) was located in `.stack-work/install/.../bin/hyraxAbif-exe` but was not being copied to the main directory
- This caused `hyraxAbif` to fail when trying to generate AB1 files

### Solution
- Modified `Dockerfile` to find and copy the actual compiled `hyraxAbif-exe` executable from `.stack-work/install` directory after building
- Used `find` command to locate the executable in the build directory structure
- Added fallback logic to check `.stack-work/dist` directory if not found in install directory
- Ensured the executable is properly copied and made executable before completing the Docker build

### Files Modified
- `Dockerfile`: Updated hyraxAbif installation section to copy the actual executable

### Testing
- Successfully tested hyraxAbif with sample02, sample03, sample04, sample05 fragments
- All 11 samples (sample02-sample12) successfully generated AB1 files
- Total of 22 AB1 files generated (2 fragments per sample)
- Verified executable size: 3.4MB (correct compiled binary)

### Verification
```bash
# Test command used:
docker run --rm -v /data/output:/data/output \
  --entrypoint bash nanopore-plasmid-pipeline:latest \
  -c '/opt/hyraxAbif/hyraxAbif-exe gen /data/output/02.fragments/sample02_2k_fragmented /data/output/03.ab1_files/test_sample02_ab1'

# Result: Successfully generated AB1 files for all samples
```

## 2025-12-03 - Fixed Step 2 Fragment Splitting Issues

### Problem
- Step 2 was finding 76 FASTA files instead of 11 (was searching in Nextflow `work/` subdirectories)
- Sample names were incorrectly extracted as `input` instead of `sample02`, `sample03`, etc.
- Output directories were created with hash names instead of sample names

### Solution
- Modified `find_fasta_files()` in `scripts/step2_split_fragments.py` to use `iterdir()` instead of `glob()` to only search top-level directory
- Fixed sample name extraction logic to properly extract from filename (e.g., `sample02.final.fasta` -> `sample02`)
- Added validation to ensure sample names start with 'sample'

### Files Modified
- `scripts/step2_split_fragments.py`

### Result
- Now correctly finds 11 FASTA files (one per sample)
- Creates properly named output directories: `sample02_2k_fragmented`, `sample03_2k_fragmented`, etc.
- Each sample's fragments are stored in its own directory

## 2025-12-03 - Docker Build Fixes and epi2me Workflow Integration

### Fixes
- **Fixed Dockerfile**:
  - Added `apt-get update` before Haskell Stack installation
  - Fixed Python package installation with `--break-system-packages` flag for Ubuntu 24.04
  - Successfully built Docker image: `nanopore-plasmid-pipeline:latest` (6.59GB)

- **Fixed epi2me samplesheet format**:
  - Updated `scripts/generate_samplesheet.py` to use correct format:
    - Columns: `barcode`, `alias`, `type` (required by epi2me wf-clone-validation)
    - Reference: https://github.com/epi2me-labs/wf-clone-validation
  - Updated `scripts/step1_run_epi2me_workflow.py`:
    - Changed `--coverage` to `--assm_coverage` (correct parameter name)
    - Updated command to use `--fastq` (parent directory) and `--sample_sheet` (CSV mapping)

### New Files
- `scripts/generate_samplesheet.py`: Generate samplesheet CSV for epi2me workflow
- `test_pipeline_remote.sh`: Test script for remote server execution
- `run_full_test.sh`: Full pipeline test script

### Testing
- Docker image successfully built on remote server
- Initialization step tested successfully
- Samplesheet generation tested successfully
- Ready for full pipeline test

## 2025-01-XX - Project Restructuring and New Workflow Design

### Major Changes

#### 1. Project Structure Reorganization
- **Archived old files**:
  - Moved `nanopore_plasmid_pipeline/` to `archive/old_pipeline/`
  - Moved old scripts (`filter_long_reads.py`, `get_length_dist.py`, etc.) to `archive/old_scripts/`
  - Moved old data files (PPTX, PNG, TXT) to `archive/old_data/`
- **Created standard directory structure**:
  - `docs/` - Documentation directory
  - `config/` - Configuration files directory
  - `templates/` - Report templates directory
  - `logs/` - Log files directory

#### 2. New Workflow Design
- **Integrated epi2me wf-clone-validation workflow**:
  - Step 1: Assembly and annotation using epi2me wf-clone-validation
  - Reference: https://github.com/epi2me-labs/wf-clone-validation
- **Fragment splitting**:
  - Step 2: Split assembled FASTA files into 2kb fragments
  - Uses existing `scripts/split_plasmid_fasta.py`
- **AB1 file generation**:
  - Step 3: Convert fragments to AB1 chromatogram files
  - Uses hyraxAbif tool
  - Installation reference: `archive/old_data/nanopore-plasmid_analysis_docker.txt`
- **Report generation**:
  - Step 4: Generate comprehensive PDF reports
  - Uses existing `scripts/generate_complete_reports.py`
- **Result summary**:
  - Step 5: Generate summary JSON and visualizations

#### 3. Documentation Updates
- **Created `README.md`**: Main project entry point with quick start guide
- **Created `docs/PIPELINE.md`**: Complete pipeline documentation
- **Created `.cursor/rules/nanopore_plasmid_assembly.mdc`**: Cursor rules for the pipeline
- **Created `CHANGE_LOGS.md`**: This file, tracking all changes

#### 4. Pipeline Architecture
- **Step-based architecture**:
  - `step0_initialize_analysis.py` - Initialization and config generation
  - `step1_run_epi2me_workflow.py` - epi2me workflow wrapper
  - `step2_split_fragments.py` - FASTA fragmentation
  - `step3_generate_ab1.py` - AB1 file generation
  - `step4_generate_reports.py` - Report generation
  - `step5_summarize_results.py` - Result summary
- **Main entry script**: `run_pipeline.py` (to be created)
- **Configuration**: `config.yaml` (auto-generated)

#### 5. Docker Integration Plan
- Planned Docker image for containerized execution
- Includes all dependencies:
  - Nextflow (for epi2me workflow)
  - hyraxAbif (Haskell-based)
  - Python 3.9+ with required packages
  - All bioinformatics tools

### Files Created
- `.cursor/rules/nanopore_plasmid_assembly.mdc`
- `README.md`
- `docs/PIPELINE.md`
- `CHANGE_LOGS.md`
- `archive/` directory structure

### Files Moved/Archived
- `nanopore_plasmid_pipeline/` → `archive/old_pipeline/`
- Old scripts → `archive/old_scripts/`
- Old data files → `archive/old_data/`

### Next Steps
- [x] Create main entry script (`run_pipeline.py`)
- [x] Implement step scripts (step0-step4)
- [x] Create Dockerfile
- [x] Create Docker documentation
- [ ] Test complete workflow
- [ ] Create usage examples

---

## 2025-01-XX - Docker Integration and Complete Pipeline Implementation

### Major Changes

#### 1. Complete Pipeline Scripts Created
- **`scripts/run_pipeline.py`**: Main entry script orchestrating all steps
- **`scripts/step0_initialize_analysis.py`**: Initialization and config generation
- **`scripts/step1_run_epi2me_workflow.py`**: epi2me wf-clone-validation wrapper
- **`scripts/step2_split_fragments.py`**: FASTA fragmentation wrapper
- **`scripts/step3_generate_ab1.py`**: AB1 file generation wrapper
- **`scripts/step4_generate_reports.py`**: Report generation wrapper

#### 2. Docker Integration
- **`Dockerfile`**: Complete Docker image definition
  - Based on Ubuntu latest
  - Includes Nextflow installation
  - Includes hyraxAbif build (Haskell Stack)
  - Includes Python dependencies
  - Copies all pipeline scripts
- **`.dockerignore`**: Excludes unnecessary files from build
- **`docker-compose.yml`**: Docker Compose configuration for easy deployment
- **`docs/DOCKER.md`**: Comprehensive Docker documentation

#### 3. Pipeline Features
- **Modular step-based architecture**: Each step can run independently
- **Skip options**: Can skip individual steps with `--skip-*` flags
- **Comprehensive logging**: All steps log to files and console
- **Error handling**: Proper error handling and validation
- **Configuration management**: YAML-based configuration

#### 4. Report Generation
- **PDF reports**: Generated using `generate_complete_reports.py`
- **JSON output**: Maintained as requested (no HTML reports)
- **Per-sample organization**: Each sample gets its own folder structure
- **Coverage plots**: Included in PDF reports
- **Read length distribution**: Included in PDF reports

### Files Created
- `scripts/run_pipeline.py`
- `scripts/step0_initialize_analysis.py`
- `scripts/step1_run_epi2me_workflow.py`
- `scripts/step2_split_fragments.py`
- `scripts/step3_generate_ab1.py`
- `scripts/step4_generate_reports.py`
- `Dockerfile`
- `.dockerignore`
- `docker-compose.yml`
- `docs/DOCKER.md`

### Files Modified
- `CHANGE_LOGS.md` - Updated with new changes

### Usage

#### Docker (Recommended)
```bash
# Build image
docker build -t nanopore-plasmid-pipeline:latest .

# Run pipeline
docker run --rm \
  -v /path/to/fast_pass:/data/input/fast_pass:ro \
  -v /path/to/output:/data/output \
  nanopore-plasmid-pipeline:latest \
  --input /data/input \
  --output /data/output \
  --project-id PROJECT_ID
```

#### Local Execution
```bash
python scripts/run_pipeline.py \
  --input fast_pass/ \
  --output output/ \
  --project-id PROJECT_ID
```

---

## Previous Changes

[Previous change logs will be added here as the project evolves]

