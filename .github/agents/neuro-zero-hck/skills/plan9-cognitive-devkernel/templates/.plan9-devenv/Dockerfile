# =============================================================================
# Plan9Cog Cognitive DevKernel — Dockerfile
# Multi-stage build: plan9port tools + QEMU for running Plan 9 / 9front
# =============================================================================

# Stage 1: Build plan9port from source
FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libx11-dev \
    libxt-dev \
    libxext-dev \
    libfontconfig1-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ARG PLAN9=/usr/local/plan9

# Clone and build plan9port (Plan 9 userspace tools for Linux)
RUN git clone --depth 1 https://github.com/9fans/plan9port.git $PLAN9 \
    && cd $PLAN9 \
    && ./INSTALL

# Stage 2: Development environment with plan9port + QEMU
FROM ubuntu:22.04 AS development

ARG PLAN9=/usr/local/plan9
ARG PLAN9_IMG=9front

RUN apt-get update && apt-get install -y --no-install-recommends \
    # QEMU for running Plan 9 / 9front natively
    qemu-system-x86 \
    qemu-utils \
    # Networking tools for 9P2000
    socat \
    netcat-openbsd \
    net-tools \
    # Development tools
    build-essential \
    git \
    curl \
    wget \
    python3 \
    python3-pip \
    # X11 libraries for plan9port GUI tools (acme, sam)
    libx11-6 \
    libxt6 \
    libxext6 \
    libfontconfig1 \
    # Editor
    vim \
    && rm -rf /var/lib/apt/lists/*

# Copy plan9port from builder
COPY --from=builder $PLAN9 $PLAN9

# Set up environment
ENV PLAN9=$PLAN9
ENV PATH="$PLAN9/bin:$PATH"

# Install Python dependencies for grid monitor
RUN pip3 install --no-cache-dir flask

# Create workspace structure
RUN mkdir -p /workspace/src \
    && mkdir -p /var/plan9/data \
    && mkdir -p /cognitive/atomspace/atoms \
    && mkdir -p /cognitive/atomspace/types \
    && mkdir -p /cognitive/atomspace/indices \
    && mkdir -p /cognitive/inference/rules \
    && mkdir -p /cognitive/inference/queue \
    && mkdir -p /cognitive/inference/results \
    && mkdir -p /cognitive/attention/bank \
    && mkdir -p /cognitive/attention/agents \
    && mkdir -p /cognitive/learning/populations \
    && mkdir -p /cognitive/learning/fitness \
    && mkdir -p /cognitive/temporal/levels \
    && mkdir -p /cognitive/temporal/phases \
    && mkdir -p /cognitive/autognosis/images \
    && mkdir -p /cognitive/autognosis/insights \
    && mkdir -p /cognitive/autognosis/metrics

WORKDIR /workspace

# Verify plan9port installation
RUN $PLAN9/bin/9 echo "Plan9port installed successfully" \
    && $PLAN9/bin/mk -version 2>&1 || true

EXPOSE 564 565 566 8080 9090
