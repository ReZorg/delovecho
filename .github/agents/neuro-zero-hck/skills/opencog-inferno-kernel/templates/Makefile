# OpenCog-Inferno Kernel Makefile
# Build system for cognitive operating system kernel

CC = gcc
CFLAGS = -Wall -Wextra -Wno-unused-parameter -O2 -g -std=c11 -pthread
LDFLAGS = -pthread

# Directories
KERNEL_DIR = kernel
TOOLS_DIR = tools
BUILD_DIR = build

# Source files
KERNEL_SRCS = $(KERNEL_DIR)/cognitive_kernel.c
TEST_SRCS = $(TOOLS_DIR)/kernel_test.c

# Object files
KERNEL_OBJS = $(BUILD_DIR)/cognitive_kernel.o
TEST_OBJS = $(BUILD_DIR)/kernel_test.o

# Targets
KERNEL_LIB = $(BUILD_DIR)/libcognitive_kernel.a
TEST_BIN = $(BUILD_DIR)/kernel_test

.PHONY: all clean test

all: $(KERNEL_LIB) $(TEST_BIN)

# Create build directory
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Build kernel library
$(KERNEL_LIB): $(KERNEL_OBJS) | $(BUILD_DIR)
	ar rcs $@ $^
	@echo "Built kernel library: $@"

# Build test program
$(TEST_BIN): $(TEST_OBJS) $(KERNEL_LIB) | $(BUILD_DIR)
	$(CC) $(LDFLAGS) -o $@ $^
	@echo "Built test program: $@"

# Compile kernel source
$(BUILD_DIR)/cognitive_kernel.o: $(KERNEL_SRCS) $(KERNEL_DIR)/cognitive_kernel.h | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

# Compile test source
$(BUILD_DIR)/kernel_test.o: $(TEST_SRCS) $(KERNEL_DIR)/cognitive_kernel.h | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

# Run tests
test: $(TEST_BIN)
	@echo "Running kernel tests..."
	@$(TEST_BIN)

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIR)
	@echo "Cleaned build directory"

# Help
help:
	@echo "OpenCog-Inferno Kernel Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all        - Build kernel library and test program (default)"
	@echo "  test       - Build and run test program"
	@echo "  clean      - Remove build artifacts"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Build artifacts:"
	@echo "  $(KERNEL_LIB) - Kernel library"
	@echo "  $(TEST_BIN)   - Test program"
