# Dove9 Cognitive Layer — Makefile.am
#
# Builds libdove9.a (static library) containing the complete cognitive
# architecture: triadic engine, kernel, DTE processor, mail bridges,
# Sys6 scheduler, and the top-level Dove9System.
#
# This is designed as a new SUBDIRS entry in src/Makefile.am.
# All dove9 C files are self-contained and don't depend on Dovecot's
# lib/ infrastructure for their core logic.

noinst_LTLIBRARIES = libdove9.la

AM_CPPFLAGS = \
	-I$(srcdir)/types \
	-I$(srcdir)/utils \
	-I$(srcdir)/cognitive \
	-I$(srcdir)/core \
	-I$(srcdir)/integration \
	-I$(srcdir)

# ---- Sources ----

libdove9_la_SOURCES = \
	utils/dove9-logger.c \
	cognitive/dove9-triadic-engine.c \
	cognitive/dove9-dte-processor.c \
	integration/dove9-mail-protocol-bridge.c \
	core/dove9-kernel.c \
	integration/dove9-orchestrator-bridge.c \
	integration/dove9-sys6-mail-scheduler.c \
	integration/dove9-sys6-orchestrator-bridge.c \
	dove9-system.c

# ---- Headers (installed for downstream consumers) ----

dove9includedir = $(includedir)/dovecho/dove9

dove9include_HEADERS = \
	types/dove9-types.h \
	utils/dove9-logger.h \
	cognitive/dove9-triadic-engine.h \
	cognitive/dove9-dte-processor.h \
	core/dove9-kernel.h \
	integration/dove9-mail-protocol-bridge.h \
	integration/dove9-orchestrator-bridge.h \
	integration/dove9-sys6-mail-scheduler.h \
	integration/dove9-sys6-orchestrator-bridge.h \
	dove9-system.h

# ---- Compile flags ----

libdove9_la_CFLAGS = -std=c11 -Wall -Wextra -Wno-unused-parameter
libdove9_la_LIBADD = -lm

# ---- Test framework ----

TEST_COMMON_SRCS = \
	test/dove9-test-common.c \
	test/dove9-test-common.h

TEST_MOCK_SRCS = \
	test/dove9-test-mocks.c \
	test/dove9-test-mocks.h

TEST_LDADD = libdove9.la -lm
TEST_CFLAGS = -std=c11 -Wall -Wextra -Wno-unused-parameter \
	-I$(srcdir)/types \
	-I$(srcdir)/utils \
	-I$(srcdir)/cognitive \
	-I$(srcdir)/core \
	-I$(srcdir)/integration \
	-I$(srcdir) \
	-I$(srcdir)/test

# ---- Test programs ----

test_programs = \
	test-dove9-types \
	test-dove9-logger \
	test-dove9-triadic-engine \
	test-dove9-dte-processor \
	test-dove9-kernel \
	test-dove9-mail-bridge \
	test-dove9-sys6-scheduler \
	test-dove9-orchestrator-bridge \
	test-dove9-sys6-bridge \
	test-dove9-system \
	test-dove9-security \
	test-dove9-integration \
	test-dove9-sys6-correctness

noinst_PROGRAMS = $(test_programs)

test_dove9_types_SOURCES = test/test-dove9-types.c $(TEST_COMMON_SRCS)
test_dove9_types_LDADD = $(TEST_LDADD)
test_dove9_types_CFLAGS = $(TEST_CFLAGS)

test_dove9_logger_SOURCES = test/test-dove9-logger.c $(TEST_COMMON_SRCS)
test_dove9_logger_LDADD = $(TEST_LDADD)
test_dove9_logger_CFLAGS = $(TEST_CFLAGS)

test_dove9_triadic_engine_SOURCES = test/test-dove9-triadic-engine.c $(TEST_COMMON_SRCS) $(TEST_MOCK_SRCS)
test_dove9_triadic_engine_LDADD = $(TEST_LDADD)
test_dove9_triadic_engine_CFLAGS = $(TEST_CFLAGS)

test_dove9_dte_processor_SOURCES = test/test-dove9-dte-processor.c $(TEST_COMMON_SRCS) $(TEST_MOCK_SRCS)
test_dove9_dte_processor_LDADD = $(TEST_LDADD)
test_dove9_dte_processor_CFLAGS = $(TEST_CFLAGS)

test_dove9_kernel_SOURCES = test/test-dove9-kernel.c $(TEST_COMMON_SRCS) $(TEST_MOCK_SRCS)
test_dove9_kernel_LDADD = $(TEST_LDADD)
test_dove9_kernel_CFLAGS = $(TEST_CFLAGS)

test_dove9_mail_bridge_SOURCES = test/test-dove9-mail-bridge.c $(TEST_COMMON_SRCS)
test_dove9_mail_bridge_LDADD = $(TEST_LDADD)
test_dove9_mail_bridge_CFLAGS = $(TEST_CFLAGS)

test_dove9_sys6_scheduler_SOURCES = test/test-dove9-sys6-scheduler.c $(TEST_COMMON_SRCS)
test_dove9_sys6_scheduler_LDADD = $(TEST_LDADD)
test_dove9_sys6_scheduler_CFLAGS = $(TEST_CFLAGS)

test_dove9_orchestrator_bridge_SOURCES = test/test-dove9-orchestrator-bridge.c $(TEST_COMMON_SRCS) $(TEST_MOCK_SRCS)
test_dove9_orchestrator_bridge_LDADD = $(TEST_LDADD)
test_dove9_orchestrator_bridge_CFLAGS = $(TEST_CFLAGS)

test_dove9_sys6_bridge_SOURCES = test/test-dove9-sys6-bridge.c $(TEST_COMMON_SRCS) $(TEST_MOCK_SRCS)
test_dove9_sys6_bridge_LDADD = $(TEST_LDADD)
test_dove9_sys6_bridge_CFLAGS = $(TEST_CFLAGS)

test_dove9_system_SOURCES = test/test-dove9-system.c $(TEST_COMMON_SRCS) $(TEST_MOCK_SRCS)
test_dove9_system_LDADD = $(TEST_LDADD)
test_dove9_system_CFLAGS = $(TEST_CFLAGS)

test_dove9_security_SOURCES = test/test-dove9-security.c $(TEST_COMMON_SRCS) $(TEST_MOCK_SRCS)
test_dove9_security_LDADD = $(TEST_LDADD)
test_dove9_security_CFLAGS = $(TEST_CFLAGS)

test_dove9_integration_SOURCES = test/test-dove9-integration.c $(TEST_COMMON_SRCS) $(TEST_MOCK_SRCS)
test_dove9_integration_LDADD = $(TEST_LDADD)
test_dove9_integration_CFLAGS = $(TEST_CFLAGS)

test_dove9_sys6_correctness_SOURCES = test/test-dove9-sys6-correctness.c $(TEST_COMMON_SRCS)
test_dove9_sys6_correctness_LDADD = $(TEST_LDADD)
test_dove9_sys6_correctness_CFLAGS = $(TEST_CFLAGS)

# ---- check-local target ----

check-local:
	@for t in $(test_programs); do \
		echo "Running $$t ..."; \
		if ./$$t; then \
			echo "PASS: $$t"; \
		else \
			echo "FAIL: $$t"; \
			exit 1; \
		fi; \
	done
	@echo "All dove9 tests passed."
