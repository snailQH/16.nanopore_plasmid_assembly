# Docker Setup and Usage

## Building the Docker Image

### Prerequisites
- Docker installed and running
- Sufficient disk space (image will be ~2-3GB)

### Build Command

```bash
# Build the image
docker build -t nanopore-plasmid-pipeline:latest .

# Or with a specific tag
docker build -t nanopore-plasmid-pipeline:v1.0 .
```

### Build Process

The Dockerfile will:
1. Install system dependencies (Ubuntu packages)
2. Install Nextflow
3. Install Haskell Stack
4. Build hyraxAbif from source
5. Install Python packages
6. Copy pipeline scripts

**Note**: Building hyraxAbif can take 10-20 minutes as it compiles Haskell code.

## Running the Pipeline

### Basic Usage

**Important**: The pipeline uses `epi2me wf-clone-validation` which requires Docker to run processes (medaka, flye, etc.). When running the pipeline inside Docker, you must:

1. Mount the Docker socket: `-v /var/run/docker.sock:/var/run/docker.sock`
2. **Set HOST_OUTPUT_DIR and HOST_INPUT_DIR environment variables** so sub-containers can access the work directory:

```bash
INPUT_DIR="/path/to/fast_pass"
OUTPUT_DIR="/path/to/output"

docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "${INPUT_DIR}:/data/input:ro" \
  -v "${OUTPUT_DIR}:/data/output" \
  -e "HOST_OUTPUT_DIR=${OUTPUT_DIR}" \
  -e "HOST_INPUT_DIR=${INPUT_DIR}" \
  nanopore-plasmid-pipeline:latest \
  --input /data/input \
  --output /data/output \
  --project-id PROJECT_ID \
  --approx-size 5000 \
  --coverage 50
```

**Why HOST_OUTPUT_DIR is required**: When Nextflow runs processes in sub-containers (Docker-in-Docker), the sub-containers need to mount the work directory from the HOST, not from inside the main container. The `HOST_OUTPUT_DIR` environment variable tells the pipeline the host path so it can correctly configure Nextflow's Docker executor.

**Note**: The `-v /var/run/docker.sock:/var/run/docker.sock` mount is required for Nextflow to use Docker containers for workflow processes when using `-profile standard`.

**Recommended**: Use the provided wrapper script `docker_run_full_pipeline.sh` which automatically sets these environment variables correctly.

### Using Docker Compose

```bash
# Edit docker-compose.yml to set input/output paths
# Then run:
docker-compose up

# Or run in background:
docker-compose up -d
```

### Example with Real Paths

```bash
docker run --rm \
  -v /mnt/data/fast_pass:/data/input/fast_pass:ro \
  -v /mnt/data/results:/data/output \
  nanopore-plasmid-pipeline:latest \
  --input /data/input \
  --output /data/output \
  --project-id UPA53974 \
  --approx-size 5000 \
  --coverage 50 \
  --fragment-size 2000
```

## Volume Mounts

### Required Mounts

1. **Input directory**: Mount your `fast_pass/` folder
   ```bash
   -v /host/path/to/fast_pass:/data/input/fast_pass:ro
   ```
   Note: `:ro` makes it read-only

2. **Output directory**: Mount where you want results
   ```bash
   -v /host/path/to/output:/data/output
   ```

### Optional Mounts

- **Config directory**: For custom config files
  ```bash
  -v /host/path/to/config:/data/config
  ```

## Running Individual Steps

You can run individual pipeline steps:

```bash
# Step 0: Initialization
docker run --rm \
  -v /path/to/fast_pass:/data/input/fast_pass:ro \
  -v /path/to/output:/data/output \
  nanopore-plasmid-pipeline:latest \
  python3 /opt/pipeline/scripts/step0_initialize_analysis.py \
    --input /data/input \
    --output /data/output \
    --project-id PROJECT_ID

# Step 1: Assembly
docker run --rm \
  -v /path/to/fast_pass:/data/input/fast_pass:ro \
  -v /path/to/output:/data/output \
  nanopore-plasmid-pipeline:latest \
  python3 /opt/pipeline/scripts/step1_run_epi2me_workflow.py \
    --config /data/output/config.yaml \
    --input /data/input \
    --output /data/output
```

## Resource Requirements

### Minimum
- CPU: 2 cores
- Memory: 4GB RAM
- Disk: 10GB free space

### Recommended
- CPU: 4-8 cores
- Memory: 8-16GB RAM
- Disk: 50GB+ free space

### For Large Datasets
- CPU: 8+ cores
- Memory: 16GB+ RAM
- Disk: 100GB+ free space

## Troubleshooting

### Issue: Build fails at hyraxAbif step

**Solution**: The build process can be slow. Try:
```bash
# Build with more verbose output
docker build --progress=plain -t nanopore-plasmid-pipeline:latest .

# Or build without cache
docker build --no-cache -t nanopore-plasmid-pipeline:latest .
```

### Issue: Permission errors

**Solution**: Ensure output directory is writable:
```bash
# Set permissions
chmod -R 777 /path/to/output

# Or run with user mapping
docker run --rm \
  -u $(id -u):$(id -g) \
  -v /path/to/output:/data/output \
  ...
```

### Issue: Nextflow workflow fails

**Solution**: Check Nextflow installation:
```bash
docker run --rm nanopore-plasmid-pipeline:latest nextflow --version
```

### Issue: hyraxAbif not found

**Solution**: Verify hyraxAbif installation:
```bash
docker run --rm nanopore-plasmid-pipeline:latest \
  ls -la /opt/hyraxAbif/hyraxAbif-exe
```

## Advanced Usage

### Interactive Shell

```bash
docker run --rm -it \
  -v /path/to/fast_pass:/data/input/fast_pass:ro \
  -v /path/to/output:/data/output \
  nanopore-plasmid-pipeline:latest \
  /bin/bash
```

### Debugging

```bash
# Run with verbose logging
docker run --rm \
  -v /path/to/fast_pass:/data/input/fast_pass:ro \
  -v /path/to/output:/data/output \
  nanopore-plasmid-pipeline:latest \
  --input /data/input \
  --output /data/output \
  --project-id PROJECT_ID \
  --verbose
```

### Custom Configuration

```bash
# Mount custom config
docker run --rm \
  -v /path/to/fast_pass:/data/input/fast_pass:ro \
  -v /path/to/output:/data/output \
  -v /path/to/custom_config.yaml:/data/config.yaml:ro \
  nanopore-plasmid-pipeline:latest \
  --input /data/input \
  --output /data/output \
  --config /data/config.yaml
```

## Image Size

The final image size is approximately:
- Base Ubuntu: ~200MB
- System packages: ~500MB
- Nextflow: ~50MB
- Haskell Stack + hyraxAbif: ~1GB
- Python packages: ~200MB
- **Total: ~2-3GB**

## Updating the Image

To update the image with new code:

```bash
# Rebuild
docker build -t nanopore-plasmid-pipeline:latest .

# Or pull updates and rebuild
git pull
docker build -t nanopore-plasmid-pipeline:latest .
```

## Best Practices

1. **Use specific tags** instead of `latest` for production
2. **Mount volumes** instead of copying data into containers
3. **Use read-only mounts** for input data (`:ro`)
4. **Set resource limits** to prevent resource exhaustion
5. **Keep logs** by mounting a log directory
6. **Use docker-compose** for complex setups

## Support

For issues or questions:
- Check logs: `docker logs <container_id>`
- Run with `--verbose` flag
- Check Docker documentation: https://docs.docker.com/

