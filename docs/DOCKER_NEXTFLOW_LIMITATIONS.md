# Docker-in-Docker Limitations with Nextflow

## Problem Summary

When running Nextflow inside a Docker container with Docker-in-Docker (Nextflow using Docker executor for processes), we encounter a fundamental limitation:

1. **File Access Issues**: Nextflow sub-containers cannot access `.command.run` files properly
2. **Docker Command Access**: `.command.run` scripts try to execute `docker` commands, but sub-containers don't have access to Docker

## Root Cause

Nextflow's Docker executor creates `.command.run` scripts that:
1. Are executed inside sub-containers (e.g., medaka, flye containers)
2. Contain logic to create additional Docker containers
3. Require Docker socket access, which is not available in sub-containers

This is a known limitation of Docker-in-Docker execution patterns with Nextflow.

## Current Status

✅ **Working:**
- Pipeline correctly detects Docker environment
- HOST_OUTPUT_DIR requirement properly enforced
- Nextflow configuration correctly generated
- File mounting configuration is correct
- Initialization and samplesheet generation work correctly

❌ **Not Working:**
- Nextflow process execution fails with:
  - `/bin/bash: .command.run: No such file or directory` (some processes)
  - `.command.run: line 292: docker: command not found` (other processes)

## Recommended Solution

**Run Nextflow on HOST, use Docker for processes** (not Docker-in-Docker):

1. Use `run_pipeline.sh` script (already implemented)
   - Runs Nextflow on the host machine
   - Nextflow uses Docker executor for processes (medaka, flye, etc.)
   - This is the standard and recommended approach

2. Alternative: Use `step1_run_epi2me_workflow_host.py`
   - Executes Nextflow in a separate Docker container on the host
   - Processes still run in Docker containers
   - Avoids nested Docker execution

## Implementation

The project already includes host execution mode:

```bash
# Use run_pipeline.sh (runs Nextflow on host)
./run_pipeline.sh \
  --input /path/to/fast_pass \
  --output /path/to/output \
  --project-id PROJECT_ID \
  --approx-size 5000 \
  --coverage 50
```

This script:
1. Runs initialization in Docker
2. Runs Nextflow on HOST (not in Docker)
3. Nextflow uses Docker executor for processes
4. Runs remaining steps in Docker

## Why This Works Better

1. **No Nested Docker Execution**: Nextflow runs on host, processes run in Docker
2. **Direct File Access**: No path mapping issues between containers
3. **Standard Pattern**: This is how Nextflow is typically used
4. **Better Performance**: No overhead of nested container execution
5. **Fewer Permission Issues**: Direct file system access

## Docker-in-Docker Alternatives (Future Work)

If Docker-in-Docker is absolutely required, possible solutions:

1. **Use DinD (Docker-in-Docker) Image**: Requires privileged mode (security risk)
2. **Use Kaniko**: Build tool that doesn't require Docker daemon (but may not work with Nextflow)
3. **Custom Nextflow Executor**: Modify Nextflow execution to avoid nested Docker calls

However, these are complex and not recommended for production use.

## Conclusion

**For production use, run Nextflow on the host machine, not inside Docker.**

The Docker-in-Docker approach has fundamental limitations that make it impractical for this use case. The existing `run_pipeline.sh` script provides the correct approach.

