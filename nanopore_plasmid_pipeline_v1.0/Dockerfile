# Nanopore Plasmid Assembly Pipeline Docker Image
# Based on Ubuntu, includes Nextflow, hyraxAbif, and Python dependencies

FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PATH="/opt/hyraxAbif:${PATH}"

# Install system dependencies
# Note: Install Docker CLI for host execution mode (running Nextflow in separate container)
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    python3 \
    python3-pip \
    python3-biopython \
    python3-matplotlib \
    build-essential \
    openjdk-17-jdk \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI (for host execution mode - running Nextflow in separate container)
# This allows the pipeline container to execute 'docker run' commands
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    rm -rf /var/lib/apt/lists/*

# Create symlink for python
RUN ln -s /usr/bin/python3 /usr/local/bin/python

# Install Nextflow (use version 23.10.0 for compatibility with epi2me workflows)
# Nextflow 25.10.2 has compilation errors with wf-clone-validation v1.8.x
# Error: Variable `metadata` already declared - this is a Nextflow version compatibility issue
# Reference: https://github.com/epi2me-labs/wf-clone-validation/issues/70
# Solution: Use NXF_VER=23.10.0 or install Nextflow 23.10.0 directly
ENV NXF_VER=23.10.0
RUN curl -fsSL https://get.nextflow.io | NXF_VER=23.10.0 bash && \
    mv nextflow /usr/local/bin/ && \
    chmod +x /usr/local/bin/nextflow && \
    nextflow -version

# Install Haskell Stack for hyraxAbif
RUN apt-get update && \
    apt-get install -y libffi-dev libgmp-dev zlib1g-dev && \
    curl -sSL https://get.haskellstack.org/ | sh && \
    stack --version

# Install hyraxAbif
WORKDIR /opt
RUN git clone https://github.com/hyraxbio/hyraxAbif.git && \
    cd hyraxAbif && \
    # Update stack.yaml with required extra-deps
    echo "extra-deps:" >> stack.yaml && \
    echo "  - stm-2.5.3.1@sha256:421b57c9cdf55b4977e9445336be3895ba0c8d92b6ec6e474f140e173270d9dd,2443" >> stack.yaml && \
    echo "  - verset-0.0.1.11" >> stack.yaml && \
    stack update && \
    STACK_YAML="stack.yaml" stack build hyraxAbif --no-run-tests && \
    make build && \
    # Find and copy the actual executable (use find to handle wildcards)
    EXE_PATH=$(find .stack-work/install -name "hyraxAbif-exe" -type f -path "*/bin/*" | head -1) && \
    if [ -n "$EXE_PATH" ] && [ -f "$EXE_PATH" ]; then \
        cp "$EXE_PATH" ./hyraxAbif-exe && \
        chmod +x hyraxAbif-exe && \
        echo "Successfully copied hyraxAbif-exe from $EXE_PATH"; \
    else \
        echo "Warning: hyraxAbif-exe not found in .stack-work/install, trying dist directory"; \
        EXE_PATH=$(find .stack-work/dist -name "hyraxAbif-exe" -type f | head -1) && \
        if [ -n "$EXE_PATH" ] && [ -f "$EXE_PATH" ]; then \
            cp "$EXE_PATH" ./hyraxAbif-exe && \
            chmod +x hyraxAbif-exe && \
            echo "Successfully copied hyraxAbif-exe from $EXE_PATH"; \
        else \
            echo "Error: hyraxAbif-exe not found in any expected location"; \
            exit 1; \
        fi; \
    fi

# Install Python packages
# Ubuntu 24.04 requires --break-system-packages flag for pip install
RUN pip3 install --no-cache-dir --break-system-packages \
    reportlab \
    numpy \
    pandas \
    pyyaml \
    beautifulsoup4

# Copy pipeline scripts
WORKDIR /opt/pipeline
COPY scripts/ /opt/pipeline/scripts/
COPY environment.yml /opt/pipeline/

# Make scripts executable
RUN chmod +x /opt/pipeline/scripts/*.py && \
    chmod +x /opt/pipeline/scripts/*.sh 2>/dev/null || true

# Set working directory
WORKDIR /data

# Set umask to ensure files created in containers are accessible by host
# This helps with permission issues when mounting volumes
RUN echo "umask 0002" >> /etc/bash.bashrc

# Set entry point
ENTRYPOINT ["python3", "/opt/pipeline/scripts/run_pipeline.py"]

# Default command
CMD ["--help"]

