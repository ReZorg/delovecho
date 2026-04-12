# Makefile — Glyph-Noetic Inferno Kernel Build System
#
# Builds the cognitive kernel modules for the Inferno-OS based
# OpenCog AGI operating system.
#
# Targets:
#   all       — Build all kernel modules
#   test      — Run the kernel test suite
#   clean     — Remove build artifacts
#   install   — Install into Inferno kernel tree
#
# Copyright (c) 2026 ManusCog Project
# License: AGPL-3.0

# ============================================================================
# Configuration
# ============================================================================

CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -g -O2
CFLAGS += -I include
CFLAGS += -DGLYPH_KERNEL_SIMULATION

# For kernel build (when integrated with Inferno):
# CC = $(INFERNO_ROOT)/Plan9/bin/cc
# CFLAGS = -I $(INFERNO_ROOT)/include

LDFLAGS = -lm

SRC_DIR = src
INC_DIR = include
BUILD_DIR = build
TEST_DIR = ../tests

# ============================================================================
# Sources
# ============================================================================

SOURCES = \
	$(SRC_DIR)/glyph.c \
	$(SRC_DIR)/temporal.c \
	$(SRC_DIR)/p9topo.c \
	$(SRC_DIR)/atomspace.c \
	$(SRC_DIR)/promises.c \
	$(SRC_DIR)/devglyph.c

HEADERS = \
	$(INC_DIR)/glyph.h

OBJECTS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(SOURCES))

# ============================================================================
# Targets
# ============================================================================

.PHONY: all test clean install

all: $(BUILD_DIR) $(BUILD_DIR)/glyph_kernel_test

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/glyph_kernel_test: $(OBJECTS) $(BUILD_DIR)/test_main.o
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

$(BUILD_DIR)/test_main.o: $(TEST_DIR)/test_main.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

test: all
	$(BUILD_DIR)/glyph_kernel_test

clean:
	rm -rf $(BUILD_DIR)

install:
	@echo "Install target requires INFERNO_ROOT to be set"
	@echo "  cp $(SRC_DIR)/*.c $(INFERNO_ROOT)/os/port/"
	@echo "  cp $(INC_DIR)/*.h $(INFERNO_ROOT)/include/"

# ============================================================================
# Python Simulation
# ============================================================================

.PHONY: sim sim-test sim-cli sim-health

sim:
	python3 ../scripts/glyph_noetic_kernel_daemon.py

sim-test:
	python3 ../scripts/glyph_noetic_kernel_daemon.py --test

sim-cli:
	python3 ../scripts/glyph_noetic_kernel_daemon.py --cli

sim-health:
	python3 ../scripts/glyph_noetic_kernel_daemon.py --health
