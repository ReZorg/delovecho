# =============================================================================
# Plan 9 Development Environment — Multi-Stage Dockerfile
# Stage 1: Build plan9port from source
# Stage 2: Development environment with plan9port + QEMU
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Builder — compile plan9port from source
# ---------------------------------------------------------------------------
FROM ubuntu:22.04 AS builder

ARG PLAN9=/usr/local/plan9
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    libx11-dev \
    libxext-dev \
    libxt-dev \
    libfontconfig1-dev \
    libfreetype-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clone and build plan9port
RUN git clone --depth 1 https://github.com/9fans/plan9port.git ${PLAN9} \
    && cd ${PLAN9} \
    && ./INSTALL

# ---------------------------------------------------------------------------
# Stage 2: Development — runtime with plan9port + QEMU + dev tools
# ---------------------------------------------------------------------------
FROM ubuntu:22.04

ARG PLAN9=/usr/local/plan9
ARG GRID_NODES=3
ARG ENABLE_GUI=true
ARG DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies and QEMU
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    git \
    jq \
    less \
    libx11-6 \
    libxext6 \
    libxt6 \
    libfontconfig1 \
    libfreetype6 \
    man-db \
    net-tools \
    python3 \
    python3-pip \
    socat \
    wget \
    # QEMU for running native Plan 9 / 9front
    qemu-system-x86 \
    qemu-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Flask for grid monitor
RUN pip3 install --no-cache-dir flask

# Copy plan9port from builder
COPY --from=builder ${PLAN9} ${PLAN9}

# Set up Plan 9 environment
ENV PLAN9=${PLAN9}
ENV PATH="${PLAN9}/bin:${PATH}"

# Create glenda user (traditional Plan 9 username)
RUN useradd -m -s /bin/bash glenda \
    && mkdir -p /workspace /var/plan9/grid \
    && chown -R glenda:glenda /workspace /var/plan9

# Create grid node directories
RUN for i in $(seq 0 $((GRID_NODES - 1))); do \
        mkdir -p /var/plan9/grid/cpu-${i}/registry; \
    done \
    && chown -R glenda:glenda /var/plan9/grid

# Verify plan9port installation
RUN ${PLAN9}/bin/9 echo "plan9port installed successfully" \
    && ls ${PLAN9}/bin/acme ${PLAN9}/bin/sam ${PLAN9}/bin/mk

# Verify QEMU installation
RUN qemu-system-x86_64 --version | head -1

WORKDIR /workspace
USER glenda

CMD ["bash"]
