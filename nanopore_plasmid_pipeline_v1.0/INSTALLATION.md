# Installation Guide - Nanopore Plasmid Assembly Pipeline

## Quick Installation

### Step 1: Prerequisites Check

```bash
# Check Docker installation
docker --version
# Should output: Docker version 20.10.x or higher

# Check Docker is running
docker ps
# Should show running containers (or empty list if no containers)

# Check disk space (need at least 10GB)
df -h
```

### Step 2: Build Docker Image

```bash
# Navigate to pipeline directory
cd nanopore_plasmid_assembly

# Build Docker image (this will take 10-30 minutes)
docker build -t nanopore-plasmid-pipeline:latest .

# Or load the image from image.tar
docker load -i nanopore-plasmid-pipeline.tar

# Monitor build progress
# You'll see output for each build step
```

**What happens during build:**
1. Downloads Ubuntu base image
2. Installs system dependencies
3. Installs Python 3.9+ and packages
4. Installs Haskell Stack
5. Builds hyraxAbif (takes longest, ~10-20 minutes)
6. Copies pipeline scripts
7. Sets up working directory

### Step 3: Verify Installation

```bash
# Test Python version
docker run --rm nanopore-plasmid-pipeline:latest python3 --version
# Expected: Python 3.9.x or higher

# Test pipeline initialization script
docker run --rm nanopore-plasmid-pipeline:latest python3 /opt/pipeline/scripts/step0_initialize_analysis.py --help
# Should show help message

# Check image size
docker images | grep nanopore-plasmid-pipeline
# Expected size: ~6.7 GB
```

## Detailed Installation

### System Requirements

#### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+) or macOS
- **Docker**: 20.10+
- **RAM**: 4GB
- **Disk**: 10GB free
- **CPU**: 2 cores

#### Recommended Requirements
- **OS**: Linux (Ubuntu 22.04+)
- **Docker**: 24.0+
- **RAM**: 8GB+
- **Disk**: 20GB+ free
- **CPU**: 4+ cores

### Docker Configuration

#### Allocate Resources (macOS/Windows)

1. Open Docker Desktop
2. Go to Settings > Resources
3. Set:
   - **CPUs**: 4+ (recommended)
   - **Memory**: 8GB+ (recommended)
   - **Disk**: 20GB+ (recommended)

#### Linux Docker Setup

```bash
# Install Docker (if not installed)
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (to run without sudo)
sudo usermod -aG docker $USER
# Log out and log back in for changes to take effect
```

### Build Process Details

#### Build Command Options

```bash
# Standard build
docker build -t nanopore-plasmid-pipeline:latest .

# Build with specific tag
docker build -t nanopore-plasmid-pipeline:v1.0 .

# Build with no cache (if having issues)
docker build --no-cache -t nanopore-plasmid-pipeline:latest .

# Build with progress output
docker build --progress=plain -t nanopore-plasmid-pipeline:latest .
```

#### Build Troubleshooting

**Issue: Build fails at hyraxAbif step**

```bash
# Solution: Increase Docker resources or build with more time
# Check Docker logs for specific error
docker build --progress=plain -t nanopore-plasmid-pipeline:latest . 2>&1 | tee build.log
```

**Issue: Out of disk space**

```bash
# Check Docker disk usage
docker system df

# Clean up unused images/containers
docker system prune -a

# Free up space and retry build
```

**Issue: Network timeout during build**

```bash
# Check internet connection
ping google.com

# Retry build (Docker will resume from last successful step)
docker build -t nanopore-plasmid-pipeline:latest .
```

**Issue: Permission denied**

```bash
# Linux: Ensure user is in docker group
groups | grep docker

# If not, add user:
sudo usermod -aG docker $USER
# Log out and back in
```

### Post-Installation Verification

#### Test Pipeline Components

```bash
# Test initialization
docker run --rm \
  -v /tmp/test_input:/data/input:ro \
  -v /tmp/test_output:/data/output \
  nanopore-plasmid-pipeline:latest \
  python3 /opt/pipeline/scripts/step0_initialize_analysis.py \
  --input /data/input \
  --output /data/output \
  --project-id TEST

# Test fragment splitting
docker run --rm \
  -v /tmp/test_fasta:/data/input:ro \
  -v /tmp/test_output:/data/output \
  nanopore-plasmid-pipeline:latest \
  python3 /opt/pipeline/scripts/step2_split_fragments.py \
  --input /data/input \
  --output /data/output \
  --fragment-size 2000

# Test AB1 generation
docker run --rm \
  -v /tmp/test_fragments:/data/input:ro \
  -v /tmp/test_output:/data/output \
  nanopore-plasmid-pipeline:latest \
  python3 /opt/pipeline/scripts/step3_generate_ab1.py \
  --input /data/input \
  --output /data/output
```

## Next Steps

After successful installation:

1. **Read User Guide**: See `docs/USER_GUIDE.md`
2. **Prepare Input Data**: Organize FASTQ files in `fast_pass/` structure
3. **Run Test**: Use small test dataset first
4. **Check Output**: Verify output structure matches expectations

## Uninstallation

```bash
# Remove Docker image
docker rmi nanopore-plasmid-pipeline:latest

# Remove all related images
docker images | grep nanopore-plasmid-pipeline | awk '{print $3}' | xargs docker rmi

# Clean up Docker system (optional)
docker system prune -a
```

## Support

For installation issues:
1. Check Docker logs: `docker build --progress=plain ...`
2. Verify system requirements
3. Check disk space and Docker resources
4. Review `CHANGE_LOGS.md` for known issues

---

**Last Updated:** 2025-12-03  
**Pipeline Version:** 1.0

