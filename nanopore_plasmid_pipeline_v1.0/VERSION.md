# Nanopore Plasmid Assembly Pipeline - Version 1.0

## Version Information

- **Version**: 1.0
- **Release Date**: 2025-12-03
- **Status**: Stable Release

## What's Included

This delivery package contains:

1. **Main Pipeline Scripts**
   - `run_pipeline.sh` - Main entry script (HOST execution)
   - `scripts/` - All Python pipeline scripts

2. **Docker Files**
   - `Dockerfile` - Docker image definition

3. **Documentation**
   - `README.md` - Project overview and quick start
   - `INSTALLATION.md` - Detailed installation guide
   - `DELIVERY_PACKAGE.md` - Package contents and structure
   - `docs/USER_GUIDE.md` - Complete user manual
   - `docs/OUTPUT_FORMAT.md` - Output file format documentation
   - `CHANGE_LOGS.md` - Version history and changes

## Quick Start

### 1. Build Docker Image

```bash
cd nanopore_plasmid_pipeline_v1.0
docker build -t nanopore-plasmid-pipeline:latest .
```

### 2. Run Pipeline

```bash
./run_pipeline.sh \
  --input /path/to/fast_pass \
  --output /path/to/output \
  --project-id PROJECT_ID \
  --approx-size 5000 \
  --coverage 50
```

## System Requirements

- **Docker**: 20.10+
- **OS**: Linux (Ubuntu 20.04+) or macOS
- **RAM**: 4GB minimum, 8GB+ recommended
- **Disk**: 10GB+ free space
- **Internet**: Required for building Docker image

## Documentation

- **Installation**: See `INSTALLATION.md`
- **User Guide**: See `docs/USER_GUIDE.md`
- **Output Format**: See `docs/OUTPUT_FORMAT.md`
- **Package Contents**: See `DELIVERY_PACKAGE.md`

## Support

For issues or questions:
1. Check `docs/USER_GUIDE.md` troubleshooting section
2. Review `CHANGE_LOGS.md` for known issues
3. Check log files in `output/logs/` directory

---

**Last Updated**: 2025-12-03  
**Pipeline Version**: 1.0

