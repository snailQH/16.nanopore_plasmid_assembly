# Using Docker Hub Image

This guide explains how to use the pre-built Docker image from Docker Hub instead of building locally.

## Prerequisites

- Docker installed and running
- Internet connection (for pulling image from Docker Hub)
- Docker Hub account (optional, for private images)

## Docker Hub Image

**Image Name**: `snailqh/nanopore-plasmid-pipeline:ampseq`  
**Image Size**: ~6.7 GB  
**Registry**: Docker Hub (hub.docker.com)

## Method 1: Pull and Use Docker Hub Image

### Step 1: Pull the Image

```bash
# Pull the image from Docker Hub
docker pull snailqh/nanopore-plasmid-pipeline:ampseq

# Verify the image
docker images | grep nanopore-plasmid-pipeline
```

### Step 2: Set Environment Variable

Before running the pipeline, set the `DOCKER_IMAGE` environment variable:

```bash
export DOCKER_IMAGE="snailqh/nanopore-plasmid-pipeline:ampseq"
```

### Step 3: Run Pipeline

```bash
./run_pipeline.sh \
  --input /path/to/fast_pass \
  --output /path/to/output \
  --project-id PROJECT_ID \
  --approx-size 5000 \
  --coverage 50
```

## Method 2: Modify run_pipeline.sh

Alternatively, you can modify the `DOCKER_IMAGE` variable in `run_pipeline.sh`:

```bash
# Edit run_pipeline.sh
# Change line 37 from:
DOCKER_IMAGE="nanopore-plasmid-pipeline:latest"

# To:
DOCKER_IMAGE="snailqh/nanopore-plasmid-pipeline:ampseq"
```

Then run the pipeline normally:

```bash
./run_pipeline.sh \
  --input /path/to/fast_pass \
  --output /path/to/output \
  --project-id PROJECT_ID
```

## Method 3: Use Docker Run Directly

You can also run the pipeline directly with Docker without using `run_pipeline.sh`:

```bash
docker run --rm \
  -v /path/to/fast_pass:/data/input/fast_pass:ro \
  -v /path/to/output:/data/output \
  snailqh/nanopore-plasmid-pipeline:ampseq \
  python3 /opt/pipeline/scripts/run_pipeline.py \
  --input /data/input/fast_pass \
  --output /data/output \
  --project-id PROJECT_ID \
  --skip-assembly  # Note: Assembly runs on HOST via run_pipeline.sh
```

**Note**: When using Docker directly, you still need to run the assembly step separately on the HOST machine using Nextflow, as described in the main documentation.

## Image Tags

Available tags:

- `ampseq` - Current stable version (recommended)
- `latest` - Latest version (if available)
- `v1.0` - Version 1.0 (if available)

```bash
# Pull specific version
docker pull snailqh/nanopore-plasmid-pipeline:ampseq
```

## Comparison: Local Build vs Docker Hub

| Feature | Local Build | Docker Hub |
|---------|-------------|------------|
| **Setup Time** | 10-30 minutes (build) | 5-10 minutes (pull) |
| **Internet Required** | Yes (for dependencies) | Yes (for pull) |
| **Disk Space** | ~6.7 GB | ~6.7 GB |
| **Customization** | Can modify Dockerfile | Fixed image |
| **Updates** | Rebuild required | `docker pull` |
| **Offline Use** | Possible after build | Requires initial pull |

## Troubleshooting

### Image Not Found

If you get an error like `Error response from daemon: pull access denied`:

1. **Check image name**: Ensure you're using the correct image name
   ```bash
   docker pull snailqh/nanopore-plasmid-pipeline:ampseq
   ```

2. **Check Docker Hub**: Verify the image exists on Docker Hub
   - Visit: https://hub.docker.com/r/snailqh/nanopore-plasmid-pipeline

3. **Login to Docker Hub** (if required):
   ```bash
   docker login
   ```

### Pull Fails Due to Network

If pulling fails due to network issues:

1. **Use mirror** (if available in your region):
   ```bash
   # Configure Docker registry mirror in /etc/docker/daemon.json
   {
     "registry-mirrors": ["https://your-mirror-url"]
   }
   ```

2. **Retry with timeout**:
   ```bash
   docker pull --platform linux/amd64 snailqh/nanopore-plasmid-pipeline:ampseq
   ```

### Verify Image Contents

After pulling, verify the image:

```bash
# Check image size
docker images snailqh/nanopore-plasmid-pipeline:ampseq

# Test Python version
docker run --rm snailqh/nanopore-plasmid-pipeline:ampseq python3 --version

# List scripts
docker run --rm snailqh/nanopore-plasmid-pipeline:ampseq ls -la /opt/pipeline/scripts/
```

## Updating the Image

To update to the latest version:

```bash
# Pull latest version
docker pull snailqh/nanopore-plasmid-pipeline:ampseq

# Remove old image (optional, saves space)
docker rmi snailqh/nanopore-plasmid-pipeline:old-tag
```

## Saving and Loading Image

If you need to transfer the image to a machine without internet:

```bash
# Save image to tar file
docker save snailqh/nanopore-plasmid-pipeline:ampseq -o nanopore-plasmid-pipeline.tar

# Load image on another machine
docker load -i nanopore-plasmid-pipeline.tar
```

## Best Practices

1. **Use specific tags** in production:
   ```bash
   DOCKER_IMAGE="snailqh/nanopore-plasmid-pipeline:ampseq"
   ```

2. **Pull before running** to ensure you have the latest version:
   ```bash
   docker pull snailqh/nanopore-plasmid-pipeline:ampseq
   ```

3. **Verify image integrity**:
   ```bash
   docker images --digests snailqh/nanopore-plasmid-pipeline:ampseq
   ```

## Example: Complete Workflow with Docker Hub

```bash
# 1. Pull image
docker pull ampseq/nanopore-plasmid-pipeline:latest

# 2. Set environment variable
export DOCKER_IMAGE="snailqh/nanopore-plasmid-pipeline:ampseq"

# 3. Run pipeline
./run_pipeline.sh \
  --input /data/fast_pass \
  --output /data/output \
  --project-id my_project \
  --approx-size 5000 \
  --coverage 50 \
  --verbose

# 4. Check results
ls -lh /data/output/04.reports/
```

---

**Last Updated**: 2025-12-03  
**Pipeline Version**: 1.0

