# Copyright (c) 2026 NVIDIA + Synopsys + Google DeepMind.
# Licensed under the Apache License, Version 2.0.

# Stage 1: EDA Build (OpenROAD & Yosys Base)
FROM ubuntu:22.04 AS eda-builder
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential cmake git tcl-dev libboost-all-dev \
    swig flex bison \
    && rm -rf /var/lib/apt/lists/*
# TODO: Clone and build OpenROAD/Yosys here.

# Stage 2: ML and Python Environment
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-devel AS ml-env
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git curl tcl tcl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root --only main

# Stage 3: Final Runtime Integration
FROM ml-env AS runtime
COPY --from=eda-builder /usr/local/bin/openroad /usr/local/bin/
COPY --from=eda-builder /usr/local/bin/yosys /usr/local/bin/
COPY . /app
RUN poetry install --only main
CMD ["python", "src/hybrid_dtco/api/server.py"]
