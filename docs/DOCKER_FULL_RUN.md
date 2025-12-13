# Running Complete Pipeline Inside Docker

## Overview

The pipeline was originally designed with a **hybrid architecture** where Nextflow runs on the HOST machine because it needs access to the Docker socket to spawn process containers (medaka, flye, etc.). However, you **CAN** run the complete pipeline inside Docker by mounting the Docker socket.

## Why the Hybrid Design?

### Original Design (HOST + Docker)
- **Nextflow on HOST**: Requires Docker socket access (`/var/run/docker.sock`)
- **Other steps in Docker**: Python scripts run in Docker containers
- **Reason**: Nextflow needs to spawn Docker containers for processes (medaka, flye, etc.)

### Full Docker Design (All in Docker)
- **All steps in Docker**: Including Nextflow
- **Requirement**: Mount Docker socket (`-v /var/run/docker.sock:/var/run/docker.sock`)
- **Benefit**: Complete containerization, easier deployment

## Running Complete Pipeline in Docker

### Method 1: Using run_pipeline.sh Inside Docker

Create a wrapper script to run `run_pipeline.sh` inside Docker:

```bash
#!/bin/bash
# Run complete pipeline inside Docker container

INPUT_DIR="/path/to/input"
OUTPUT_DIR="/path/to/output"
PROJECT_ID="PROJECT_ID"

docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "${INPUT_DIR}:/data/input:ro" \
  -v "${OUTPUT_DIR}:/data/output" \
  -v "$(pwd):/opt/pipeline:ro" \
  -w /opt/pipeline \
  --entrypoint /bin/bash \
  nanopore-plasmid-pipeline:latest \
  -c "./run_pipeline.sh \
      --input /data/input \
      --output /data/output \
      --project-id ${PROJECT_ID} \
      --approx-size 5000 \
      --coverage 50"
```

### Method 2: Using run_pipeline.py (Recommended)

The `run_pipeline.py` script is designed to run inside Docker and can handle Nextflow execution:

```bash
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "${INPUT_DIR}:/data/input:ro" \
  -v "${OUTPUT_DIR}:/data/output" \
  nanopore-plasmid-pipeline:latest \
  --input /data/input \
  --output /data/output \
  --project-id PROJECT_ID \
  --approx-size 5000 \
  --coverage 50
```

**Note**: The script will:
1. Detect that it's running inside Docker
2. Use Nextflow installed in the image
3. Access Docker socket for process containers

### Method 3: Modify run_pipeline.sh to Support Docker-In-Docker

You can modify `run_pipeline.sh` to detect if it's running inside Docker and adjust paths accordingly:

```bash
# Check if running inside Docker
if [[ -f /.dockerenv ]] || [[ -n "${DOCKER_CONTAINER:-}" ]]; then
    # Running inside Docker
    # Use container paths and Docker socket
    DOCKER_SOCKET="/var/run/docker.sock"
    if [[ ! -S "$DOCKER_SOCKET" ]]; then
        echo "ERROR: Docker socket not found. Mount it with: -v /var/run/docker.sock:/var/run/docker.sock"
        exit 1
    fi
    # Use Nextflow from container
    NEXTFLOW_CMD="nextflow"
else
    # Running on HOST
    # Use host paths and check for Nextflow installation
    # ... existing logic ...
fi
```

## Requirements for Docker-In-Docker

1. **Docker Socket Mount**: `-v /var/run/docker.sock:/var/run/docker.sock`
   - Allows container to spawn child containers
   - Required for Nextflow's `-profile standard` (uses Docker)

2. **Docker CLI in Container**: The Docker image includes Docker CLI (see Dockerfile line 36)

3. **Nextflow in Container**: Nextflow is installed in the Docker image (see Dockerfile line 48-51)

4. **Volume Mounts**: Mount input/output directories as needed

## Example: Complete Docker Run

```bash
#!/bin/bash
# Complete pipeline execution in Docker

INPUT_DIR="/home/user/data/fast_pass"
OUTPUT_DIR="/home/user/results"
PROJECT_ID="my_project"

docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "${INPUT_DIR}:/data/input:ro" \
  -v "${OUTPUT_DIR}:/data/output" \
  nanopore-plasmid-pipeline:latest \
  --input /data/input \
  --output /data/output \
  --project-id ${PROJECT_ID} \
  --approx-size 5000 \
  --coverage 50 \
  --verbose
```

## Current Implementation Status

### What Works Now:
- ✅ Steps 0, 2-4: Run inside Docker via `run_pipeline.py`
- ✅ Step 1 (Nextflow): Can run inside Docker IF Docker socket is mounted
- ✅ `run_pipeline.sh`: Currently assumes HOST execution

### What Needs Modification:
- ⚠️ `run_pipeline.sh`: Needs to detect Docker environment and adjust paths
- ⚠️ Nextflow execution: Currently assumes HOST, but can work in Docker with socket

## Recommendations

### For Development/Testing:
Use `run_pipeline.sh` on HOST (current design) - simpler, easier to debug

### For Production/Deployment:
Use `run_pipeline.py` in Docker with Docker socket mounted - fully containerized

### For CI/CD:
Use Docker-in-Docker approach with socket mounting for reproducible builds

## Troubleshooting

### Error: "Cannot connect to Docker daemon"
**Solution**: Mount Docker socket: `-v /var/run/docker.sock:/var/run/docker.sock`

### Error: "Nextflow not found"
**Solution**: Use the Docker image which includes Nextflow, or mount Nextflow binary

### Error: "Permission denied" on Docker socket
**Solution**: Ensure Docker group permissions allow socket access:
```bash
sudo chmod 666 /var/run/docker.sock
# Or add user to docker group
sudo usermod -aG docker $USER
```

## Summary

**Yes, you can run the complete pipeline inside Docker**, including Nextflow. The original hybrid design was chosen for simplicity and compatibility, but full Docker execution is possible and recommended for deployment scenarios.

The key requirement is mounting the Docker socket (`-v /var/run/docker.sock:/var/run/docker.sock`) to allow Nextflow to spawn process containers.

