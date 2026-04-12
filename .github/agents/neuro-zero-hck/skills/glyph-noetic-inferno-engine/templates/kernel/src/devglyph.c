/*
 * devglyph.c — /dev/glyph Character Device Driver
 *
 * Implements the Inferno kernel character device that provides
 * the primary user-space interface to the Glyph-Noetic Engine.
 *
 * Usage from Limbo or shell:
 *   echo '[C:PLN]?' > /dev/glyph    # Execute a noetic sentence
 *   cat /dev/glyph                    # Read the result
 *   echo '[T:ASSEMBLY]?' > /dev/glyph
 *   cat /dev/glyph
 *
 * The device driver translates file I/O operations into glyph
 * dispatch calls, making the cognitive engine accessible through
 * the standard Plan 9 file interface.
 *
 * Inferno Device Table Entry:
 *   Dev glyphdevtab = {
 *       'G',
 *       "glyph",
 *       devreset,
 *       devglyph_init,
 *       devattach,
 *       devwalk,
 *       devstat,
 *       devglyph_open,
 *       devcreate,
 *       devglyph_close,
 *       devglyph_read,
 *       devbread,
 *       devglyph_write,
 *       devbwrite,
 *       devremove,
 *       devwstat,
 *   };
 *
 * Copyright (c) 2026 ManusCog Project
 * License: AGPL-3.0
 */

#include "glyph.h"
#include <stdio.h>
#include <string.h>

/* ============================================================================
 * Device State
 * ============================================================================ */

/*
 * Per-channel state for the /dev/glyph device.
 * Each open file descriptor gets its own response buffer,
 * allowing concurrent access from multiple processes.
 */
typedef struct DevGlyphChan {
    GlyphResult *last_result;    /* Result of last write operation */
    int          result_offset;  /* Read cursor into result data */
} DevGlyphChan;

/* Maximum concurrent channels */
#define MAX_GLYPH_CHANS 64
static DevGlyphChan channels[MAX_GLYPH_CHANS];
static int num_channels = 0;

/* ============================================================================
 * Device Initialization
 * ============================================================================ */

void
devglyph_init(void)
{
    GlyphEngine *engine;

    printf("[devglyph] Initializing /dev/glyph character device\n");

    /* Initialize the cognitive engine */
    engine = glyph_engine_init();
    if (engine == NULL) {
        printf("[devglyph] FATAL: Failed to initialize glyph engine\n");
        return;
    }

    /* Run initial autognosis cycle */
    autognosis_build_self_image(engine);

    memset(channels, 0, sizeof(channels));
    num_channels = 0;

    printf("[devglyph] /dev/glyph ready (engine v%s, %d glyphs)\n",
           engine->version, engine->num_glyphs);
}

/* ============================================================================
 * Device Read — Retrieve the result of the last noetic sentence
 * ============================================================================ */

/*
 * devglyph_read — Called when a process reads from /dev/glyph.
 *
 * Returns the JSON result of the most recently executed noetic
 * sentence for this channel. If no sentence has been executed,
 * returns the engine status.
 *
 * The read is non-blocking and returns whatever data is available.
 * Multiple reads will continue from where the last read left off,
 * allowing large results to be read incrementally.
 */
long
devglyph_read(void *chanptr, void *buf, long n, long long offset)
{
    GlyphEngine *engine = glyph_engine_get();
    DevGlyphChan *dchan = (DevGlyphChan *)chanptr;
    GlyphResult *result;
    long avail, tocopy;

    if (engine == NULL)
        return -1;

    /* If no result from a previous write, return engine status */
    if (dchan == NULL || dchan->last_result == NULL) {
        result = glyph_result_new();
        if (result == NULL)
            return -1;

        /* Default: return engine status */
        GlyphSentence sentence;
        glyph_parse_sentence("[K:STATUS]?", &sentence);
        glyph_dispatch(engine, &sentence, result);

        long len = result->data_len;
        if (len > n)
            len = n;
        memcpy(buf, result->data, len);
        glyph_result_free(result);
        return len;
    }

    /* Return data from the last result */
    result = dchan->last_result;
    avail = result->data_len - dchan->result_offset;
    if (avail <= 0)
        return 0;

    tocopy = (avail < n) ? avail : n;
    memcpy(buf, result->data + dchan->result_offset, tocopy);
    dchan->result_offset += tocopy;

    return tocopy;
}

/* ============================================================================
 * Device Write — Execute a noetic sentence
 * ============================================================================ */

/*
 * devglyph_write — Called when a process writes to /dev/glyph.
 *
 * The written data is interpreted as a noetic sentence (e.g.,
 * "[C:PLN]?", "[T:ASSEMBLY]?", "[T~g] -> [C:PLN]").
 *
 * The sentence is parsed, dispatched to the appropriate glyph
 * handler, and the result is stored for subsequent reads.
 *
 * Returns the number of bytes consumed (always the full write).
 */
long
devglyph_write(void *chanptr, void *buf, long n, long long offset)
{
    GlyphEngine *engine = glyph_engine_get();
    DevGlyphChan *dchan = (DevGlyphChan *)chanptr;
    GlyphSentence sentence;
    GlyphResult *result;
    char raw[GLYPH_MAX_SENTENCE];

    if (engine == NULL)
        return -1;

    /* Copy and null-terminate the input */
    long len = (n < GLYPH_MAX_SENTENCE - 1) ? n : GLYPH_MAX_SENTENCE - 1;
    memcpy(raw, buf, len);
    raw[len] = '\0';

    /* Strip trailing newline */
    if (len > 0 && raw[len - 1] == '\n')
        raw[len - 1] = '\0';

    /* Parse the noetic sentence */
    if (glyph_parse_sentence(raw, &sentence) != 0) {
        /* If parsing fails, try treating the whole string as a glyph ID */
        memset(&sentence, 0, sizeof(sentence));
        strncpy(sentence.primary_glyph, raw, GLYPH_MAX_ID_LEN - 1);
        sentence.op = '?';
    }

    /* Allocate result */
    result = glyph_result_new();
    if (result == NULL)
        return -1;

    /* Dispatch */
    glyph_dispatch(engine, &sentence, result);

    /* Store result for subsequent reads */
    if (dchan != NULL) {
        if (dchan->last_result)
            glyph_result_free(dchan->last_result);
        dchan->last_result = result;
        dchan->result_offset = 0;
    } else {
        glyph_result_free(result);
    }

    /* Advance the temporal scheduler (each write is a cognitive event) */
    temporal_tick(engine);

    return n;
}

/* ============================================================================
 * Device Close
 * ============================================================================ */

void
devglyph_close(void *chanptr)
{
    DevGlyphChan *dchan = (DevGlyphChan *)chanptr;

    if (dchan != NULL) {
        if (dchan->last_result)
            glyph_result_free(dchan->last_result);
        dchan->last_result = NULL;
        dchan->result_offset = 0;
    }
}
