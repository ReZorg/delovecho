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
